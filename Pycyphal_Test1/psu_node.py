import os
import sys
import asyncio
import logging
import traceback

# Show detailed logs to console immediately
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# Keep your existing dsdl path insertion
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "cyvenv", "dsdl_out"))

import pycyphal  # noqa: E402
import uavcan    # noqa: E402
from pycyphal.application import make_node
from pycyphal.transport.udp import UDPTransport
from uavcan.node import Health_1_0, Mode_1_0, Version_1_0, GetInfo_1_0
from uavcan.si.unit.voltage import Scalar_1_0 as Voltage_1_0

NODE_ID = 42
VIN_ID, VOUT_ID = 1200, 1201

async def main():
    try:
        logger.debug("Starting main()")
        logger.debug("pycyphal version: %s", getattr(pycyphal, "__version__", "unknown"))
        logger.debug("uavcan version: %s", getattr(uavcan, "__version__", "unknown"))

        logger.debug("Creating node...")
        node = make_node(
            transport=UDPTransport("127.0.0.1"),
            info=GetInfo_1_0.Response(
                protocol_version=Version_1_0(1, 0),
                software_version=Version_1_0(1, 0),
                name="warak.psu",
            ),
        )
        logger.debug("Node created: %r", node)

        # Ensure ID is set before starting
        node.registry.setdefault("uavcan.node.id", NODE_ID)
        logger.debug("Registry uavcan.node.id set to %s", NODE_ID)

        # Await start explicitly (clearer than checking iscoroutine)
        logger.debug("Starting node (await node.start())...")
        node.start()
        logger.debug("node.start() completed")

        # Configure heartbeat; do NOT call .start() (not present in this pycyphal version)
        node.heartbeat_publisher.mode = Mode_1_0.OPERATIONAL
        node.heartbeat_publisher.health = Health_1_0.NOMINAL
        logger.debug("Heartbeat configured: mode=%s health=%s", node.heartbeat_publisher.mode, node.heartbeat_publisher.health)

        pub_vin = node.make_publisher(Voltage_1_0, VIN_ID)
        pub_vout = node.make_publisher(Voltage_1_0, VOUT_ID)
        logger.debug("Publishers created: vin=%r vout=%r", pub_vin, pub_vout)

        try:
            logger.info("Entering publish loop")
            while True:
                await pub_vin.publish(Voltage_1_0(volt=230.0))
                await pub_vout.publish(Voltage_1_0(volt=24.0))
                await asyncio.sleep(0.5)
        finally:
            logger.debug("Leaving publish loop: closing node")
            mc = node.close()
            if asyncio.iscoroutine(mc):
                await mc
            logger.debug("Node closed")
    except Exception:
        # Print full traceback to console so you see why it might be "blank"
        logger.error("Unhandled exception in main():\n%s", traceback.format_exc())
        raise

if __name__ == "__main__":
    # Run and show traceback if event loop fails to start
    try:
        logger.debug("Calling asyncio.run(main())")
        asyncio.run(main())
    except Exception:
        logger.critical("Exception while running asyncio.run:\n%s", traceback.format_exc())
        # Ensure process doesn't silently die without output
        sys.exit(1)
