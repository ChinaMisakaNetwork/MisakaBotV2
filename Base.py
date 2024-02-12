from pydantic import BaseModel
import json


class Config(BaseModel):
    def dumps(self):
        dic = {}
        for key in self.__dict__:
            dic[key] = getattr(self, key)
        return json.dumps(dic)

    def save(self, filename):
        f = open(filename, "w")
        f.write(self.dumps())
        f.close()