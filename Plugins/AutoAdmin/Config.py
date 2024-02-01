from pydantic import BaseModel


class ScopedConfig(BaseModel):
    enabled: bool = True
    domain: str = "*"
    priority: int = 50
    blacklist_message: str = "BLACKLISTED_MESSAGE"


class Config(BaseModel):
    admin: ScopedConfig
