"""Singularion Nexus Node - Entry point for running a mesh node."""

import argparse
import asyncio
import logging
import signal
import yaml
from pathlib import Path
from .orchestrator import NexusOrchestrator, NexusConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> NexusConfig:
    path = Path(config_path)
    if not path.exists():
        logger.warning(f"Config not found: {config_path}, using defaults")
        return NexusConfig()
    with open(path) as f:
        data = yaml.safe_load(f)
    return NexusConfig(**{k: v for k, v in data.items() if hasattr(NexusConfig, k)})


async def run_node(config: NexusConfig) -> None:
    orchestrator = NexusOrchestrator(config)
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)
    await orchestrator.start()
    logger.info("Node running. Press Ctrl+C to stop.")
    await stop_event.wait()
    await orchestrator.stop()


def main():
    parser = argparse.ArgumentParser(description="Singularion Nexus Node")
    parser.add_argument("--config", default="configs/dev.yaml")
    parser.add_argument("--node-id", default=None)
    args = parser.parse_args()
    config = load_config(args.config)
    if args.node_id:
        config.node_id = args.node_id
    asyncio.run(run_node(config))

if __name__ == "__main__":
    main()
