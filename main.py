import nonebot
from nonebot.adapters.onebot import V11Adapter
from nonebot import logger

# Initialization
nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(V11Adapter)

nonebot.load_plugin("Database")

config = driver.config
for pluginDir in driver.config.plugin_dir:
    nonebot.load_plugins(pluginDir)

logger.success("Plugins have been loaded.")

if __name__ == "__main__":
    nonebot.run(app = "__mp_main__:app")