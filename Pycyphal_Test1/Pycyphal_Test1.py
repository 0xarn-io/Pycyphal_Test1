import os, sys, time
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "cyvenv", "dsdl_out"))
import pycyphal, uavcan
from pycyphal.application import make_node
from pycyphal.transport.udp import UDPTransport
from uavcan.node import Health_1_0, Mode_1_0, Version_1_0, GetInfo_1_0, Heartbeat_1_0
from uavcan.si.unit.voltage import Scalar_1_0 as Voltage_1_0

TRANSPORT = "UDP,127.0.0.1"
NODE_ID = 42
VIN_ID, VOUT_ID = 1200, 1201

async def main() -> None:
    # Build UDP transport for localhost
    transport = UDPTransport("127.0.0.1")
    
    # Node info for GetInfo_1_0 service
    info = GetInfo_1_0.Response(
        protocol_version=Version_1_0(major=1, minor=0),
        software_version=Version_1_0(major=1, minor=0),
        name="warak.psu",
    )
    
    # Create node
    node = make_node(transport=transport, info=info)
    
    # Set Node-ID via register before starting
    node.registry.setdefault("uavcan.node.id", NODE_ID)
    
    # Start the node (enables heartbeat, GetInfo, etc.)
    node.start()
    
    # Create publishers
    pub_vin = node.make_publisher(Voltage_1_0, VIN_ID)
    pub_vout = node.make_publisher(Voltage_1_0, VOUT_ID)
    heartbeat_publisher = node.make_publisher(Heartbeat_1_0, 7509)  # Heartbeat uses port-ID 0 by convention
    
    print(f"UP on UDP as Node-ID {NODE_ID} → VIN@{VIN_ID}, VOUT@{VOUT_ID}")
    
    try:
        uptime = 0
        while True:
            # Publish voltage messages
            await pub_vin.publish(Voltage_1_0(volt=230.0))
            await pub_vout.publish(Voltage_1_0(volt=24.0))
            
            # Publish heartbeat every 1 second (Cyphal spec recommends ~1 Hz)
            if uptime % 2 == 0:  # Since loop runs every 0.5s, this gives ~1 Hz
                # corrected heartbeat construction
                heartbeat_msg = Heartbeat_1_0(
                    uptime=uptime // 2,
                    health=Health_1_0(Health_1_0.NOMINAL),
                    mode=Mode_1_0(Mode_1_0.OPERATIONAL),
                    vendor_specific_status_code=0,
                )
                await heartbeat_publisher.publish(heartbeat_msg)
            
            print(f"Published: VIN=230V, VOUT=24V, Heartbeat uptime={uptime // 2}")
            uptime += 1
            await asyncio.sleep(0.5)  # Yield to event loop
    except asyncio.CancelledError:
        pass
    finally:
        node.close()

if __name__ == "__main__":
    asyncio.run(main())