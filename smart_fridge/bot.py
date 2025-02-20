import asyncio
import logging

from smart_fridge.bot.app import BotApp


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s   %(name)-25s %(levelname)-8s %(message)s",
    )

    bot = BotApp()
    await bot.run()


if __name__ == "__main__":
    asyncio.run(main())
