from Base import Config as ConfigBase
from typing import List, Union

class Config(ConfigBase):
    enabled: bool = False
    domain: List[Union[int, str]] = ["*"]
    priority: int = 50
    reject: bool = True
    kick: bool = True
    hint: bool = True
    blacklist_message: str = "BLACKLISTED_MESSAGE"

    mute_super_priv: int = 3
    mute_approve: int = 2
    mute_cancel_after: int = 1800