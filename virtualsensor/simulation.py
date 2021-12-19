from time import time
from tkinter.font import names
from typing import List, Any
import matplotlib.pyplot as plt
from time import sleep


class SensorRequest:
    sensor_name: str
    column_name: str

    def __init__(self, sensor_name, column_name):
        self.sensor_name = sensor_name
        self.column_name = column_name

    def __str__(self):
        return f"SensorRequest(sensor_name={self.sensor_name}, column_name={self.column_name})"


class SimulationEvent:
    name: str
    time: float

    def __init__(self, name: str, event_time: float):
        self.name = name
        self.time = event_time

    def __str__(self):
        return f"SimulationEvent(name={self.name}, time={self.time})"


class SimulationEventGoal:
    event: SimulationEvent
    time_margin: float
    met: bool = False
    missed: bool = False
    met_at: float = None

    def __init__(self, event: SimulationEvent, time_margin: float = 1):
        self.event = event
        self.time_margin = time_margin

    def __str__(self):
        return f"SimulationEventGoal(event={self.event}, time_margin={self.time_margin}, met={self.met})"


class Simulation:
    """
    This Simulation object should be inherited by your implementation of a Simulation to feed the Arduino with
    relevant sensor data and listen for SimulationEventGoals
    """
    name: str = "UNNAMED SIMULATION"
    start_time: float = None  # in seconds
    finish_time: float = None  # in seconds
    running: bool = False

    goals: List[SimulationEventGoal] = []

    sent_data: dict = {}

    time_scalar: float = 1  # makes the simulation run faster or slower... use for testing only

    def start(self, run_for: float = None):
        """
        Starts the simulation.
        """
        self.running = True
        self.start_time = time()
        print(f"Started simulation: {self.name}")
        if run_for:
            sleep(run_for / self.time_scalar)
            self.finish()

    def finish(self):
        """
        Stops the simulation.
        """
        self.running = False
        self.finish_time = time()
        print(f"Finished simulation: {self.name}")

    def get_time_elapsed(self) -> float:
        """
        If the simulation has not yet started, returns 0

        If the simulation has finished, returns the time that the simulation finished

        :return: The amount of time elapsed since the start of the simulation
        :rtype: float
        """
        if not self.start_time:
            return 0
        if self.finish_time:
            return self.finish_time
        return (time() - self.start_time) * self.time_scalar

    def _get_value(self, request: SensorRequest) -> Any:
        """
        Internal method to call self.get_value but do logging and recording of the data that is sent
        """
        value = self.get_value(request)
        if self.running:
            item = self.sent_data.setdefault(request.column_name, {})
            item.setdefault("x", []).append(self.get_time_elapsed())
            item.setdefault("y", []).append(value)
        return value

    def get_value(self, request: SensorRequest) -> Any:
        """
        This method should be overridden by subclasses of Simulation. It defines what values are returned by the
        Simulation, based on the contents of the SensorRequest and the time since the start of the simulation, obtained
        with Simulation#get_time_elapsed()

        :param request: The SensorRequest object
        :type request: SensorRequest
        :return: The output of the Simulation to the Arduino based on the input parameters
        """
        return 0

    def process_event(self, event: SimulationEvent) -> bool:
        """
        the Arduino can emit events at various points in a Simulation. We process them here, and determine if
        any SimulationEventGoals are met for this Simulation.

        :param event: The SimulationEvent received from the Arduino
        :type event: SimulationEvent
        :return: Whether or not the SimulationEvent corresponds to a SimulationEventGoal that was met
        :rtype: bool
        """
        for goal in self.goals:
            print(f"Got event {event}")
            if event.name == goal.event.name and not (goal.met or goal.missed):  # determine if the unmet goal is of the same event name
                # determine if the time of the SimulationEvent is within the margin specified in the SimulationEventGoal
                goal.met = goal.event.time - goal.time_margin <= event.time <= goal.event.time + goal.time_margin
                time_elapsed = self.get_time_elapsed()
                goal.met_at = time_elapsed
                if goal.met:
                    print(f"[{time_elapsed}] Goal met: {goal}")
                else:
                    goal.missed = True
                    print(f"[{time_elapsed}] Goal missed: {goal}")
                return goal.met

    def add_goal(self, goal: SimulationEventGoal) -> List[SimulationEventGoal]:
        """
        Add a SimulationEventGoal to the Simulation

        :param goal: The SimulationEventGoal to add
        :type goal: SimulationEventGoal
        :return: The updated list of SimulationEventGoals for this Simulation
        :rtype: List[SimulationEventGoal]
        """

        self.goals.append(goal)
        print(f"{self.name}: Added goal {goal}")
        return self.goals

    def plot_results(self):
        axes = plt.gca()  # get current axis
        column_names = self.sent_data.keys()
        if not column_names:
            print("No data to plot")
            return
        for column_name in column_names:
            data = self.sent_data[column_name]
            plt.plot(data["x"], data["y"], label=column_name + " (simulated)", marker=".")
        for goal in self.goals:
            color = "green" if goal.met else "red"
            plt.axvline(
                x=goal.event.time,
                color="black",
                linestyle="dashed"
            )
            plt.axvline(
                x=goal.event.time + goal.time_margin,
                color=color,
                linestyle="dashed"
            )
            plt.axvline(
                x=goal.event.time - goal.time_margin,
                color=color,
                linestyle="dashed"
            )
            plt.axvspan(
                goal.event.time - goal.time_margin,
                goal.event.time + goal.time_margin,
                alpha=0.1,
                color=color
            )
            if goal.met or goal.missed:
                plt.axvline(
                    x=goal.met_at,
                    color="blue",
                    linestyle="solid"
                )
            bottom, top = axes.get_ylim()
            plt.text(
                x=goal.event.time + (goal.time_margin / 3),
                y=(top - bottom) * 0.1,
                s=goal.event.name,
                rotation="vertical",
                va="center"
            )
            if goal.missed:
                plt.text(
                    x=goal.met_at + (goal.time_margin / 3),
                    y=(top - bottom) * 0.1,
                    s=goal.event.name,
                    rotation="vertical",
                    va="center"
                )
        plt.legend()
        plt.title(f"Simulation Results - {self.name}")
        plt.xlabel("Time (seconds)")
        plt.grid()

    def __str__(self):
        return f"Simulation(name={self.name}, start_time={self.start_time})"
