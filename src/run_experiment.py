from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path

import numpy as np
import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer

from metrics import compute_metrics


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def safe_slug(value: str) -> str:
    return value.replace("/", "__").replace(" ", "_")


def render_chat(tokenizer, messages, add_generation_prompt: bool):
    if getattr(tokenizer, "chat_template", None):
        return tokenizer.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=add_generation_prompt,
            return_tensors="pt",
        )

    # Fallback for models without a chat template.
    chunks = []
    for m in messages:
        chunks.append(f"{m['role'].upper()}: {m['content']}")
    if add_generation_prompt:
        chunks.append("ASSISTANT:")
    text = "\n\n".join(chunks)
    return tokenizer(text, return_tensors="pt").input_ids


def decode_new_tokens(tokenizer, generated, prompt_len: int) -> str:
    new_tokens = generated[0, prompt_len:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def conversation_state(model, tokenizer, messages, max_state_tokens: int = 64):
    """Return a compact last-layer representation of the current conversation.

    We use the mean of the final `max_state_tokens` hidden states. This is a
    deliberately simple preregisterable summary, not a claim that it isolates an
    emotion representation.
    """
    ids = render_chat(tokenizer, messages, add_generation_prompt=False).to(model.device)
    with torch.inference_mode():
        out = model(input_ids=ids, output_hidden_states=True, use_cache=False)
    h = out.hidden_states[-1][0]
    h = h[-min(max_state_tokens, h.shape[0]) :]
    return h.float().mean(dim=0).cpu().numpy()


def run_condition(model, tokenizer, config, condition_name: str, seed: int, output_root: Path):
    shared = config["shared"]
    condition = config["conditions"][condition_name]
    content_prompts = config["content_prompts"]
    interpersonal = condition["interpersonal_turns"]

    if len(content_prompts) != len(interpersonal):
        raise ValueError(
            f"{condition_name}: expected equal content/interpersonal turns, got "
            f"{len(content_prompts)} and {len(interpersonal)}"
        )

    set_seed(seed)
    messages = [{"role": "system", "content": shared["system_prompt"]}]
    records = []
    states = []

    for turn_index, (social_text, content_text) in enumerate(zip(interpersonal, content_prompts), start=1):
        user_text = f"{social_text}\n\n{content_text}"
        messages.append({"role": "user", "content": user_text})

        input_ids = render_chat(tokenizer, messages, add_generation_prompt=True).to(model.device)
        prompt_len = input_ids.shape[-1]

        with torch.inference_mode():
            generated = model.generate(
                input_ids=input_ids,
                do_sample=shared["temperature"] > 0,
                temperature=max(float(shared["temperature"]), 1e-6),
                top_p=float(shared["top_p"]),
                max_new_tokens=int(shared["max_new_tokens"]),
                pad_token_id=tokenizer.eos_token_id,
            )

        response = decode_new_tokens(tokenizer, generated, prompt_len)
        messages.append({"role": "assistant", "content": response})

        state = conversation_state(model, tokenizer, messages)
        states.append(state)

        record = {
            "condition": condition_name,
            "condition_label": condition["label"],
            "seed": seed,
            "turn": turn_index,
            "interpersonal_text": social_text,
            "content_prompt": content_text,
            "response": response,
            "metrics": compute_metrics(response),
        }
        records.append(record)

    out_dir = output_root / condition_name
    out_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = out_dir / f"seed_{seed}.jsonl"
    with jsonl_path.open("w", encoding="utf-8") as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    np.save(out_dir / f"seed_{seed}_states.npy", np.stack(states, axis=0))
    return jsonl_path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/conditions.yaml")
    parser.add_argument("--model", default=os.getenv("MODEL_ID"))
    parser.add_argument("--condition", default="all")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--output", default="results/raw")
    parser.add_argument("--token", default=os.getenv("HF_TOKEN1"))
    args = parser.parse_args()

    if not args.model:
        raise SystemExit("Set --model or MODEL_ID to an instruction-tuned Hugging Face model.")

    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    tokenizer = AutoTokenizer.from_pretrained(args.model, token=args.token)
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        token=args.token,
        torch_dtype="auto",
        device_map="auto",
    )
    model.eval()

    conditions = list(config["conditions"])
    if args.condition != "all":
        if args.condition not in config["conditions"]:
            raise SystemExit(f"Unknown condition: {args.condition}")
        conditions = [args.condition]

    seeds = [args.seed] if args.seed is not None else list(config["shared"]["seeds"])
    output_root = Path(args.output) / safe_slug(args.model)

    manifest = {
        "model": args.model,
        "config": args.config,
        "conditions": conditions,
        "seeds": seeds,
        "torch": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    for condition_name in conditions:
        for seed in seeds:
            path = run_condition(model, tokenizer, config, condition_name, seed, output_root)
            print(path)


if __name__ == "__main__":
    main()
