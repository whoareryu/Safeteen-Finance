from apps.titanic.app.models.rose_model import RoseModel
from apps.titanic.app.repositories.walter_reader import WalterReader


class JackService:
    def __init__(self):
        self.walter = WalterReader()
        self.rose = RoseModel()

    def get_data(self):
        return self.walter.get_data()

    def get_count(self):
        return self.walter.get_count()

    def get_count_survived(self):
        return self.walter.get_count_survived()

    def get_count_dead(self):
        return self.walter.get_count_dead()
    
    def has_decision_tree_model(self):
        return self.rose.has_decision_tree_model()

    def get_training_model_name(self) -> str:
        return self.rose.get_training_model_name()

    def get_training_model_accuracy(self) -> float:
        df = self.walter.get_full_dataframe()
        return self.rose.compute_training_accuracy(df)
