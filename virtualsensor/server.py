from serial.tools.list_ports import comports
from serial.tools.list_ports_common import ListPortInfo
from serial import Serial
from typing import List
from threading import Thread
import colorama
from colorama import Fore, Back, Style
from enum import Enum
from virtualsensor.simulation import Simulation, SensorRequest, SimulationEvent


class CommandName(str, Enum):
    ISTEST = "ISTEST"
    SENSOR_REQUEST = "REQ"
    LOG = "LOG"
    EVENT = "EVENT"


def list_available_ports():
    ports: List[ListPortInfo] = comports()
    print(", ".join([port.name for port in ports]))


def log(text):
    print(Fore.YELLOW + str(text))


class VirtualSensorServer:
    serial: Serial
    io_thread: Thread
    prefix: str = "@VS:"
    sep: str = ":"
    debug: bool
    sensors_to_test: List[str]
    simulation: Simulation
    serial_monitor: bool = True

    _run_thread: bool = False

    def __init__(self, port: str, sensors_to_test: List[str], simulation: Simulation, baud_rate=115200,
                 debug=False, serial_monitor: bool = True):
        self.debug = debug  # turn debug mode on or off
        self.sensors_to_test = sensors_to_test
        self.simulation = simulation
        self.serial_monitor = serial_monitor
        colorama.init(autoreset=True)
        colorama.ansi.clear_screen()
        self.serial = Serial(port, baud_rate)

    def start(self):
        self.io_thread = Thread(target=self.receive_line)
        self._run_thread = True
        self.io_thread.start()

    def stop(self):
        self._run_thread = False

    def receive_line(self):
        while self._run_thread:
            line = self.serial.readline().decode().strip("\n\r ")
            if line.startswith(self.prefix):
                print(Fore.CYAN + line) if self.debug else ""
                self.process_command(line.removeprefix(self.prefix))
            else:
                print(line) if self.serial_monitor else ""
        self.serial.close()

    def send_line(self, line: str):
        log(line) if self.debug else ""  # log output of server to Arduino
        self.serial.write((line + "\n").encode())

    def process_command(self, command: str):
        __args = command.split(self.sep)
        command_name = __args[0]
        args = __args[1:]

        if command_name == CommandName.ISTEST:
            # example: @VS:ISTEST:BME280
            sensor_name: str = args[0]
            if sensor_name in self.sensors_to_test:
                self.send_line("true")
            else:
                self.send_line("false")

        if command_name == CommandName.SENSOR_REQUEST:
            request = SensorRequest(*args)
            log(request) if self.debug else ""
            value = self.simulation._get_value(request)
            self.send_line(str(value))

        if command_name == CommandName.EVENT:
            event = SimulationEvent(args[0], self.simulation.get_time_elapsed())
            self.simulation.process_event(event)


if __name__ == "__main__":
    list_available_ports()
    sim = Simulation()
    VirtualSensorServer("COM5", ["BME280"], simulation=sim, debug=True)

