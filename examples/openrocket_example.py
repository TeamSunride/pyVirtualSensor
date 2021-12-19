from virtualsensor import *

sim = OpenRocketSimulation(
    "../OpenRocketSimulation_SRM_1-5.csv",
    ["APOGEE"],
    goal_margin=3
)

server = VirtualSensorServer(
    "COM5",
    ["BME280"],
    simulation=sim,
    serial_monitor=False
)

server.start()
sleep(2)

sim.time_scalar = 100
sim.start(run_for=500)

server.stop()

sim.plot_results()
plt.show()
