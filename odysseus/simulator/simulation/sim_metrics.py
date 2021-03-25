class SimMetrics:

    def __init__(self, metrics_dict):
        self.metrics_dict = metrics_dict
        self.metrics_values = dict()
        for metrics in self.metrics_dict:
            if self.metrics_dict[metrics] == "sum":
                self.metrics_values[metrics] = 0

            elif self.metrics_dict[metrics] == "min":
                self.metrics_values[metrics] = float('inf')

            elif self.metrics_dict[metrics] == "max":
                self.metrics_values[metrics] = float('-inf')

            elif self.metrics_dict[metrics] == "avg":
                self.metrics_values[metrics] = {}
                self.metrics_values[metrics]["tot"] = 0
                self.metrics_values[metrics]["count"] = 0

    def update_metrics(self, metrics, value):
        if self.metrics_dict[metrics] == "sum":
            self.metrics_values[metrics] += value

        elif self.metrics_dict[metrics] == "min":
            if value < self.metrics_values[metrics]:
                self.metrics_values[metrics] = value

        elif self.metrics_dict[metrics] == "max":
            if value > self.metrics_values[metrics]:
                self.metrics_values[metrics] = value

        elif self.metrics_dict[metrics] == "avg":
            self.metrics_values[metrics]["tot"] += value
            self.metrics_values[metrics]["count"] += 1

    def metrics_iter(self):
        for metrics in self.metrics_dict:
            if self.metrics_dict[metrics] == "avg":
                if self.metrics_values[metrics]["count"]:
                    yield metrics, self.metrics_values[metrics]["tot"] / self.metrics_values[metrics]["count"]
                else:
                    yield metrics, "ND"
            else:
                yield metrics, self.metrics_values[metrics]
