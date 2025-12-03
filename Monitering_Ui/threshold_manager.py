import json
import os

class ThresholdManager:
    FILE_PATH = os.path.join(os.path.dirname(__file__), "thresholds.json")

    def __init__(self):
        self.thresholds = {}
        self.load()

    def load(self):
        try:
            with open(self.FILE_PATH, "r", encoding="utf-8") as f:
                self.thresholds = json.load(f)
        except FileNotFoundError:
            self.thresholds = {}
            self.save()

    def save(self):
        with open(self.FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.thresholds, f, indent=4, ensure_ascii=False)

    def get_threshold(self, table, column):
        th = self.thresholds.get(table, {}).get(column)
        if not th:
            return None

        # Backward compatibility
        return {
            "lower_yellow": th.get("lower_yellow"),
            "lower_red": th.get("lower_red"),
            "upper_yellow": th.get("upper_yellow") or th.get("yellow"),
            "upper_red": th.get("upper_red") or th.get("red"),
        }

    def set_threshold(self, table, column, ly, lr, uy, ur):
        if table not in self.thresholds:
            self.thresholds[table] = {}

        self.thresholds[table][column] = {
            "lower_yellow": ly,
            "lower_red": lr,
            "upper_yellow": uy,
            "upper_red": ur
        }
        self.save()
