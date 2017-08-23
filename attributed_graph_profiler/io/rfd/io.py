import pandas as pd
from attributed_graph_profiler.io.csv.io import CSVInputOutput


class RFDInputOutput:
    csv_io = CSVInputOutput()

    def load(self, path: str) -> pd.DataFrame:
        return self.csv_io.load(path=path)

