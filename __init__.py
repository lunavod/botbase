from bot import Bot
from config import ConfigBunker, ConfigTabun

tabun_bot = Bot(ConfigTabun())
tabun_bot.run()
bunker_bot = Bot(ConfigBunker())
bunker_bot.run()
input()
tabun_bot.stop()
bunker_bot.stop()
