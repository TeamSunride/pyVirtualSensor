from virtualsensor import *
from math import sin
from time import sleep

from virtualsensor.simulation import Simulation, SensorRequest


class MySimulation(Simulation):
    name = "Tom's simulation"

    def get_value(self, request: SensorRequest):
        time_since_start = self.get_time_elapsed()
        return sin(time_since_start)


sim = MySimulation()
server = VirtualSensorServer("COM5", ["BME280"], simulation=sim, debug=False, serial_monitor=False)
server.start()
sleep(2)

sim.start(run_for=10)
server.stop()
sim.plot_results()
plt.show()
