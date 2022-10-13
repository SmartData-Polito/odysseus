class SimMetrics:

    def __init__(self):

        self.metrics_dict = {
            "cum_relo_ret_t": "sum",
            "min_vehicles_relocated": "min",  # Minimum number of vehicles relocated at the same time
            "max_vehicles_relocated": "max",  # Maximum number of vehicles relocated at the same time
            "avg_relocation_step_distance": "avg",
            "tot_vehicles_moved": "sum",
        }
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

            elif self.metrics_dict[metrics] == "list":
                self.metrics_values[metrics] = list()

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

        elif self.metrics_dict[metrics] == "list":
            self.metrics_values[metrics].append(value)

    def metrics_iter(self):
        for metrics in self.metrics_dict:
            if self.metrics_dict[metrics] == "avg":
                if self.metrics_values[metrics]["count"]:
                    yield metrics, self.metrics_values[metrics]["tot"] / self.metrics_values[metrics]["count"]
                else:
                    yield metrics, "NA"
            else:
                yield metrics, self.metrics_values[metrics]
