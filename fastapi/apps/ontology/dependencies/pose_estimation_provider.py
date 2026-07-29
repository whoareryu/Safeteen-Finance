from functools import lru_cache

from core.matrix.secret_manager import secret_manager
from ontology.adapter.outbound.resource_adapters.pose_estimation.vitpose_model_adapter import (
    VitPoseModelAdapter,
)
from ontology.app.ports.input.pose_estimation_use_case import PoseEstimationUseCase
from ontology.app.ports.output.pose_estimation_model_port import PoseEstimationModelPort
from ontology.app.use_cases.pose_estimation_interactor import PoseEstimationInteractor


@lru_cache(maxsize=1)
def get_pose_estimation_model_port() -> PoseEstimationModelPort:
    # 가중치 로드 비용이 커서 요청마다 새로 만들지 않고 캐싱한다.
    model_id = secret_manager.get_secret("POSE_ESTIMATION_MODEL_ID", "usyd-community/vitpose-base-simple")
    device = secret_manager.get_secret("POSE_ESTIMATION_DEVICE", "cpu")
    return VitPoseModelAdapter(model_id=model_id, device=device)


def get_pose_estimation_use_case() -> PoseEstimationUseCase:
    return PoseEstimationInteractor(model=get_pose_estimation_model_port())
