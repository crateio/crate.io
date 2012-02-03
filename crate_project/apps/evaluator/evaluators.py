

class EvaluationSuite(object):

    def __init__(self):
        self.evaluators = []

    def register(self, cls):
        self.evaluators.append(cls)

    def unregister(self, cls):
        try:
            self.evaluators.remove(cls)
        except ValueError:
            pass

    def evaluate(self, obj):
        for test in self.evaluators:
            evaluator = test()
            result = evaluator.evaluate(obj)
            result.update({"evaluator": evaluator})
            yield result


suite = EvaluationSuite()
