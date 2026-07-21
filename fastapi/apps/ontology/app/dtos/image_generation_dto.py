from dataclasses import dataclass


@dataclass(frozen=True)
class ImageGenerateCommand:

    prompt: str
    negative_prompt: str | None = None
    num_inference_steps: int = 1
    guidance_scale: float = 0.0


@dataclass(frozen=True)
class ImageGenerateResult:

    image_url: str
    seed: int
    steps: int
    model: str
