from setuptools import setup, find_packages

requirements = open("requirements.txt").read().split("\n")[:-1]

setup(
    name="pyVirtualSensor",
    version=0.1,
    description="Python library to pass simulated data to VirtualSensors and run testing of scenarios that would "
                "otherwise be difficult to test",
    url="https://github.com/TeamSunride/pyVirtualSensor",
    packages=find_packages("virtualsensor"),
    install_requires=requirements,
    zip_safe=False
)
