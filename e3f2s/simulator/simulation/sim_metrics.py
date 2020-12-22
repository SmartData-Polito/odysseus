class SimMetrics:

    def __init__(self, metrics_dict):
        self.metrics_dict = metrics_dict
        self.metrics_values = dict()
        for metrics in self.metrics_dict:
            if self.metrics_dict[metrics] == "sum":
                self.metrics_values[metrics] = 0

    def update_metrics(self, metrics, value):
        if self.metrics_dict[metrics] == "sum":
            self.metrics_values[metrics] += value
