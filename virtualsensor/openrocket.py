import re
import pandas as pd
from typing import List
from virtualsensor.simulation import *
from pandas import DataFrame

event_regex = r" (?P<event_name>[A-Z_]+)* occurred at t=(?P<time>[\d\.]+) seconds"


class OpenRocketDataParser:
    data_dict: dict = {}
    data_table: pd.DataFrame = DataFrame()
    events: List[SimulationEvent] = []

    def __init__(self, file_name):
        with open(file_name, newline='') as f:
            lines = f.readlines()
            column_names = lines[0]

            # format column names into snake_case
            column_names = [item[:item.rfind(" ")].replace(" ", "_").replace("(", "").replace(")", "").lower()
                            for item in column_names.strip("# \n").split(",")]

            data = {}  # construct dictionary from data

            for line in lines[1:]:
                if line.startswith("#"):  # is a comment
                    matches = re.search(event_regex, line)
                    event = SimulationEvent(matches.group("event_name"), float(matches.group("time")))
                    if event.name and event.time:  # the comment describes an event
                        print(event)
                        self.events.append(event)
                    continue

                i = 0
                for value in line.split(","):
                    column_name = column_names[i]
                    data.setdefault(column_name, []).append(float(value))
                    i += 1

            self.data_table = pd.DataFrame(data)

            self.data_table["air_pressure"] *= 100  # convert air pressure to pascals

    def plot_all(self):
        self.data_table.plot()

    def get_table(self) -> DataFrame:
        return self.data_table

    def get_dict(self) -> dict:
        return self.data_dict

    def get_events(self) -> List[SimulationEvent]:
        return self.events


class OpenRocketSimulation(Simulation):
    name = "Unnamed OpenRocket Simulation"
    parser: OpenRocketDataParser
    goal_margin: float

    def __init__(self, file_name: str, goal_names: List[str], goal_margin: float = 1):
        self.goal_margin = goal_margin
        self.parser = OpenRocketDataParser(file_name)
        for event in self.parser.events:
            if event.name in goal_names:
                goal = SimulationEventGoal(event, self.goal_margin)
                self.add_goal(goal)

    def get_value(self, request: SensorRequest) -> Any:
        time_elapsed = self.get_time_elapsed()
        df = self.parser.data_table

        if request.column_name not in df.columns:
            print(f"Warning: {request.column_name} not in OpenRocket data, returning 0")
            return 0

        return df[df["time"] >= time_elapsed].iloc[0][request.column_name]


if __name__ == "__main__":
    pass
