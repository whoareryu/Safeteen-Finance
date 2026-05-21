from apps.titanic.app.services.jack_service import JackService


class JamesController:
    def __init__(self):
        self.service = JackService()

    def get_data(self):
        return self.service.get_data()

    def get_count(self):
        return self.service.get_count()

    def get_count_survived(self):
        return self.service.get_count_survived()

    def get_count_dead(self):
        return self.service.get_count_dead()

    def has_decision_tree_model(self):
        return self.service.has_decision_tree_model()

    def get_training_model_name(self):
        return self.service.get_training_model_name()

    def get_training_model_accuracy(self):
        return self.service.get_training_model_accuracy()
