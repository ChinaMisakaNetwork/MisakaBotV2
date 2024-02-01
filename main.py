import nonebot
from nonebot.adapters.console import Adapter as ConsoleAdapter
from nonebot import logger

# Initialization
nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ConsoleAdapter)

config = driver.config
for pluginDir in driver.config.plugin_dir:
    nonebot.load_plugins(pluginDir)

logger.success("Plugins have been loaded.")

nonebot.run()