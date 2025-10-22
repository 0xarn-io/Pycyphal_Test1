import os, sys, time
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "cyvenv", "dsdl_out"))
import pycyphal, uavcan
from pycyphal.application import make_node
from pycyphal.transport.udp import UDPTransport
from uavcan.node import Health_1_0, Mode_1_0, Version_1_0, GetInfo_1_0, Heartbeat_1_0
from uavcan.si.unit.voltage import Scalar_1_0 as Voltage_1_0
