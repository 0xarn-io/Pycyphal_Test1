import os, sys, asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "cyvenv", "dsdl_out"))

import pycyphal, uavcan
from pycyphal.application import make_node
from pycyphal.transport.udp import UDPTransport
from uavcan.node import Version_1_0, GetInfo_1_0, Heartbeat_1_0
from uavcan.si.unit.voltage import Scalar_1_0 as Voltage_1_0

NODE_ID = 43  # different from the publisher node
VIN_ID, VOUT_ID = 1200, 1201

async def main():
    # Create a UDP-based node
    node = make_node(
        transport=UDPTransport("127.0.0.1"),
        info=GetInfo_1_0.Response(
            protocol_version=Version_1_0(1, 0),
            software_version=Version_1_0(1, 0),
            name="warak.psu_monitor",
        ),
    )
    node.registry.setdefault("uavcan.node.id", NODE_ID)

    maybe = node.start()
    if asyncio.iscoroutine(maybe):
        await maybe

    # Create subscribers
    sub_hb   = node.make_subscriber(Heartbeat_1_0, 7509)
    sub_vin  = node.make_subscriber(Voltage_1_0, VIN_ID)
    sub_vout = node.make_subscriber(Voltage_1_0, VOUT_ID)

    async def listen_heartbeat():
        async for msg, meta in sub_hb:
            print(f"[Heartbeat] Node {meta.source_node_id:>3}: uptime={msg.uptime:>5}s "
                  f"health={msg.health.value} mode={msg.mode.value}")

    async def listen_voltage(sub, name):
        async for msg, meta in sub:
            print(f"[{name}] from Node {meta.source_node_id:>3}: {msg.volt:.2f} V")

    # Run all listeners concurrently
    tasks = [
        asyncio.create_task(listen_heartbeat()),
        asyncio.create_task(listen_voltage(sub_vin, "VIN")),
        asyncio.create_task(listen_voltage(sub_vout, "VOUT")),
    ]

    print(f"PSU Monitor node running on UDP as Node-ID {NODE_ID}")
    print("Listening for 7509 (Heartbeat), 1200 (VIN), 1201 (VOUT) ...")

    try:
        await asyncio.Event().wait()  # run forever
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        for t in tasks:
            t.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        maybe = node.close()
        if asyncio.iscoroutine(maybe):
            await maybe

if __name__ == "__main__":
    asyncio.run(main())
