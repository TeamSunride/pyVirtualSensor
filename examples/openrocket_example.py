from virtualsensor import *

sim = OpenRocketSimulation(
    "../OpenRocketSimulation_SRM_1-5.csv",
    ["APOGEE"],
    goal_margin=3
)

server = VirtualSensorServer(
    "COM3",
    ["BME280"],
    simulation=sim,
    serial_monitor=True,
    debug=True,
    baud_rate=2000000
)

server.start()

sim.time_scalar = 100
sim.start(run_for=500)

server.stop()

sim.plot_results()
plt.show()
