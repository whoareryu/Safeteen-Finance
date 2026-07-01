from core.lol.t1_mid_faker_orchestrator import T1MidFakerOrchestrator

_MODEL = "exaone3.5:2.4b"


def get_chef_llm() -> T1MidFakerOrchestrator:
    """chef 스포크 전용 LLM — exaone3.5:2.4b."""
    return T1MidFakerOrchestrator(model=_MODEL)
