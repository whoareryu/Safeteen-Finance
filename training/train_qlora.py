"""EXAONE-3.5-2.4B-Instruct QLoRA 파인튜닝.

사용 예:
    python train_qlora.py \
        --base-model ./models/EXAONE-3.5-2.4B-Instruct \
        --dataset ./data/train.jsonl \
        --output-dir ./outputs/exaone-2.4b-qlora

--dataset는 JSONL, 각 줄 {"text": "..."} 형식(완성된 학습용 프롬프트+응답 문자열).
"""

from __future__ import annotations

import argparse
import inspect

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, masking_utils
from trl import SFTConfig, SFTTrainer

# EXAONE의 trust_remote_code 커스텀 코드(modeling_exaone.py)가 create_causal_mask를
# 구버전 개발판 시그니처(input_embeds=, cache_position= 포함)로 호출하는데, 설치된
# transformers의 실제 시그니처는 inputs_embeds=이고 cache_position 인자 자체가 없다.
# modeling_exaone.py가 `from transformers.masking_utils import create_causal_mask`로
# 모델 로딩 시점에 이름을 가져오므로, from_pretrained 호출 전에 여기서 옛 키워드를
# 지금 시그니처에 맞게 정리해 받아주도록 감싼다.
_original_create_causal_mask = masking_utils.create_causal_mask
_valid_params = set(inspect.signature(_original_create_causal_mask).parameters)


def _create_causal_mask_compat(*args, **kwargs):
    if "input_embeds" in kwargs:
        kwargs["inputs_embeds"] = kwargs.pop("input_embeds")
    kwargs = {k: v for k, v in kwargs.items() if k in _valid_params}
    return _original_create_causal_mask(*args, **kwargs)


masking_utils.create_causal_mask = _create_causal_mask_compat


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", required=True, help="EXAONE-3.5-2.4B-Instruct 로컬 경로 또는 HF repo id")
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

    tokenizer = AutoTokenizer.from_pretrained(args.base_model, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.base_model,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    # transformers 5.x의 get_input_embeddings 기본 자동탐지는 백본 속성명이
    # "model"인 경우만 처리하는데, EXAONE은 "transformer"를 쓴다(_tied_weights_keys
    # 참고). 자동탐지가 실패해 get_output_embeddings()도 덩달아 None을 반환하고,
    # trl의 SFTTrainer가 그 결과로 lm_head.weight에 접근하다 죽는다. 실제 속성
    # (transformer.wte, lm_head)에 맞춰 인스턴스에 직접 바인딩한다.
    model.get_input_embeddings = lambda: model.transformer.wte
    model.get_output_embeddings = lambda: model.lm_head
    model = prepare_model_for_kbit_training(model)

    lora_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        # EXAONE은 LLaMA 계열과 동일한 모듈명을 쓴다(q_proj/k_proj/v_proj/o_proj +
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
