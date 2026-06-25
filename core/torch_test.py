# 2. 파이토치 라이브러리를 불러옵니다.

import torch

# 3. GPU(MPS)만 사용합니다.
#    맥북(Apple Silicon)은 CUDA가 없고 MPS(Metal) 백엔드를 사용합니다.
#    MPS를 쓸 수 없으면 CPU로 넘어가지 않고 에러로 멈춥니다.

assert torch.backends.mps.is_available(), "MPS(GPU)를 사용할 수 없습니다."
device = torch.device("mps")

print("사용 device:", device)

# 4. 실제로 GPU(MPS)에서 연산이 되는지 간단히 확인합니다.

x = torch.rand(3, 3, device=device)
print(x)
