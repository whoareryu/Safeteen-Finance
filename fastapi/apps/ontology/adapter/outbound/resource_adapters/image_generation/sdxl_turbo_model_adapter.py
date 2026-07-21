from __future__ import annotations

import io
import logging

import torch
from diffusers import AutoPipelineForText2Image

from ontology.app.dtos.image_generation_dto import ImageGenerateCommand
from ontology.app.ports.output.image_generation_model_port import ImageGenerationModelPort

logger = logging.getLogger(__name__)


class SdxlTurboModelAdapter(ImageGenerationModelPort):
    """Stable Diffusion XL Turbo(+선택적 LoRA) 텍스트→이미지 생성 어댑터.

    가중치는 허깅페이스 허브에서 최초 호출 시 캐시로 내려받는다(수 GB) — 배포 환경에
    미리 다운로드해두지 않으면 첫 요청이 느리다.
    """

    def __init__(
        self,
        model_id: str = "stabilityai/sdxl-turbo",
        lora_weights_path: str | None = None,
        device: str = "cpu",
    ) -> None:
        self._model_id = model_id
        self._device = device
        dtype = torch.float16 if device in ("mps", "cuda") else torch.float32

        self._pipe = AutoPipelineForText2Image.from_pretrained(
            model_id, torch_dtype=dtype
        ).to(device)

        if lora_weights_path:
            self._pipe.load_lora_weights(lora_weights_path)
            logger.info("LoRA 어댑터 로드 완료: %s", lora_weights_path)

        logger.info("이미지 생성 모델 로드 완료: %s (device=%s)", model_id, device)

    def generate(self, command: ImageGenerateCommand) -> tuple[bytes, int]:
        seed = torch.seed() & 0xFFFFFFFF
        generator = torch.Generator(device=self._device).manual_seed(seed)

        result = self._pipe(
            prompt=command.prompt,
            negative_prompt=command.negative_prompt,
            num_inference_steps=command.num_inference_steps,
            guidance_scale=command.guidance_scale,
            generator=generator,
        )
        image = result.images[0]

        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return buf.getvalue(), seed

    def model_name(self) -> str:
        return self._model_id
