from dataclasses import dataclass

@dataclass
class AddUserFile:

    async def execute(self):
        raise NotImplementedError
