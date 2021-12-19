from virtualsensor.server import VirtualSensorServer
from virtualsensor.simulation import *
from time import sleep
from math import sin

plt.style.use("ggplot")


class MySimulation(Simulation):
    name = "Tom's simulation"

    def get_value(self, request: SensorRequest):
        return self.get_time_elapsed() + sin(self.get_time_elapsed()) * 0.1


sim = MySimulation()

event = SimulationEvent(name="TEMP_ABOVE_5", event_time=5)
goal = SimulationEventGoal(event)
goal.time_margin = 0.5
sim.add_goal(goal)

event2 = SimulationEvent(name="TEMP_ABOVE_7", event_time=7)
goal2 = SimulationEventGoal(event2)
goal2.time_margin = 0.5
sim.add_goal(goal2)

server = VirtualSensorServer("COM5", ["BME280"], simulation=sim, debug=False, serial_monitor=False)
server.start()
sleep(2)  # wait for arduino to start

sim.time_scalar = 10
sim.start(run_for=10)
server.stop()
print(", ".join([str(goal) for goal in sim.goals]))
print(sim.sent_data)
sim.plot_results()
plt.show()
