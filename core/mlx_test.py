# 2. MLX 라이브러리를 불러옵니다.

import mlx.core as mx

# 3. GPU(Metal)만 사용합니다.
#    MLX는 Apple Silicon 전용이라 기본 장치가 GPU지만, 명시적으로 GPU로 고정합니다.

mx.set_default_device(mx.gpu)
device = mx.default_device()

print("사용 device:", device)

# 4. 실제로 GPU(Metal)에서 연산이 되는지 간단히 확인합니다.

x = mx.random.uniform(shape=(3, 3))
mx.eval(x)
print(x)