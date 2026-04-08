"""Singularion Nexus Node — Entry point."""

import argparse
import asyncio
import logging
import signal
from pathlib import Path
from .orchestrator import NexusOrchestrator, NexusConfig

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> NexusConfig:
    path = Path(config_path)
    if not path.exists():
        return NexusConfig()
    try:
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return NexusConfig(**{k: v for k, v in data.items() if hasattr(NexusConfig, k)})
    except ImportError:
        return NexusConfig()


async def run_node(config: NexusConfig) -> None:
    orch = NexusOrchestrator(config)
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()
    for s in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(s, stop_event.set)
    await orch.start()
    await stop_event.wait()
    await orch.stop()


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
