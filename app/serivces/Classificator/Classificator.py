from typing import List


class Classificator:

    def __init__(self, strategy):
        self.classify = strategy

    def classify(self, **kwargs) -> int:
        return self.classify(**kwargs)
