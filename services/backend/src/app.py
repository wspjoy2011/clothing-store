import asyncio

from settings.logging_config import get_logger

logger = get_logger(__name__, "app")


async def main():
    while True:
        logger.info("App is running...")
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("App stopped.")
