from pydantic import BaseModel
from typing import List, Union
import json

class Config(BaseModel):
    enabled: bool = False
    domain: List[Union[int, str]] = ["*"]
    priority: int = 50
    blacklist_message: str = "BLACKLISTED_MESSAGE"

    def dumps(self):
        dic = {}
        for key in self.__dict__:
            dic[key] = getattr(self, key)
        return json.dumps(dic)