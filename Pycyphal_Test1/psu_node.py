import os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "cyvenv", "dsdl_out"))

from pycyphal.application import make_node
from pycyphal.transport.udp import UDPTransport
from uavcan.node import Health_1_0, Mode_1_0, Version_1_0, GetInfo_1_0
from uavcan.si.unit.voltage import Scalar_1_0 as Voltage_1_0

TRANSPORT = "UDP,127.0.0.1"
NODE_ID = 42
VIN_ID, VOUT_ID = 1200, 1201

def main():
    # Build UDP transport bound to the local host interface.
    transport = UDPTransport("127.0.0.1")        # can be your NIC IP instead of loopback

    info = GetInfo_1_0.Response(
        protocol_version=Version_1_0(major=1, minor=0),
        software_version=Version_1_0(major=1, minor=0),
        name="warak.psu",
    )

    node = make_node(transport=transport, info=info)

    # Set Node-ID via register BEFORE start()
    node.registry.setdefault("uavcan.node.id", NODE_ID)

    node.start()  # heartbeat, GetInfo/ExecuteCommand, registers, port list

    node.heartbeat_publisher.mode.value   = Mode_1_0.OPERATIONAL
    node.heartbeat_publisher.health.value = Health_1_0.NOMINAL

    pub_vin  = node.make_publisher(Voltage_1_0, VIN_ID)
    pub_vout = node.make_publisher(Voltage_1_0, VOUT_ID)

    print(f"UP on UDP as Node-ID {NODE_ID} → VIN@{VIN_ID}, VOUT@{VOUT_ID}")
    try:
        while True:
            pub_vin.publish(Voltage_1_0(volt=230.0))
            pub_vout.publish(Voltage_1_0(volt=24.0))
            node.spin(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()

if __name__ == "__main__":
    main()