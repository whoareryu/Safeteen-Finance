from chef.app.chef_orchestrator import get_chef_llm
from chef.app.use_cases.classify_spam_interactor import ClassifySpamInteractor


def get_spam_use_case() -> ClassifySpamInteractor:
    return ClassifySpamInteractor(llm=get_chef_llm())
