from dataclasses import dataclass


@dataclass
class FileRegistrationData:
    hash: bytes
    presentation_name: str
