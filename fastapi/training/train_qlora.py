"""Qwen3-4B-Instruct QLoRA 파인튜닝.

사용 예:
    python train_qlora.py \
        --base-model ./models/Qwen3-4B-Instruct-2507 \
        --dataset ./data/train.jsonl \
        --output-dir ./outputs/qwen3-4b-qlora

--dataset는 JSONL, 각 줄 {"text": "..."} 형식(완성된 학습용 프롬프트+응답 문자열).
"""

from __future__ import annotations

import argparse

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", required=True, help="Qwen3-4B-Instruct 로컬 경로 또는 HF repo id")
    parser.add_argument("--dataset", required=True, help="학습 데이터 JSONL 경로 ({'text': ...} 줄 단위)")
    parser.add_argument("--output-dir", required=True, help="LoRA 어댑터 저장 경로")
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=8)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=32)
    parser.add_argument("--max-seq-len", type=int, default=1024)
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=bnb_config,
        device_map="auto",
    )
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        # Qwen3도 LLaMA 계열과 동일한 모듈명을 쓴다(q_proj/k_proj/v_proj/o_proj +
        # gate_proj/up_proj/down_proj). "all-linear"를 쓰면 tie_word_embeddings=True라
        # 입력 임베딩과 묶여 있는 lm_head까지 어댑터 대상에 들어가 병합 시 문제가 될 수
        # 있어, lm_head를 뺀 어텐션·MLP 프로젝션 레이어만 명시적으로 지정한다.
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj",
            "gate_proj", "up_proj", "down_proj",
        ],
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    dataset = load_dataset("json", data_files=args.dataset, split="train")

    sft_config = SFTConfig(
        output_dir=args.output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        bf16=True,
        logging_steps=10,
        save_strategy="epoch",
        max_length=args.max_seq_len,
        dataset_text_field="text",
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=dataset,
        processing_class=tokenizer,
    )
    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)


if __name__ == "__main__":
    main()
