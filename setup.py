from distutils.core import setup
from glob import glob  # Needed for the examples below only

import setuptools

from energy_usage import VERSION

setup(
    name="energy-usage",
    version=VERSION,
    description="Records realtime energy usage from a Glowmarkt MQTT feed into influxdb",
    author="Ben Roberts",
    author_email="me@benroberts.net",
    url="https://gitlab.sihnon.net/ben/energy-usage",

    # Distribute all python packages within this repository except tests
    packages=setuptools.find_packages(exclude=['tests*']),

    # If necessary, include non-python files stored in your package
    package_data={
        'energy_usage': ['config_default.yaml'],
    },

    # Because the package contains non-python files, it must be installed
    # in uncompressed format, not as a zip-format .egg file
    zip_safe=False,

    # Executable scripts
    # Wrappers will be automatically generated using the correct python shebang
    # to run the methods indicated
    entry_points={
        'console_scripts': [
            'energy-usage=energy_usage.main:main',
        ]
    },

    # Extra content like lib directories, config files from outside of the package
    data_files=[
        ('/etc/energy-usage/config.yaml.example', ['config.yaml.example']),
    ],

    install_requires=[
        'confuse~=1.3',
        'influxdb~=5.3',
        'paho-mqtt~=1.5',
    ]
)
