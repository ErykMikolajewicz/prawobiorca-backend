from dataclasses import dataclass


@dataclass
class DocumentToEmbed:
    title: str | None
    text: str
