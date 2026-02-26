from dataclasses import dataclass


@dataclass
class Point:
    number: int
    body: str


@dataclass
class Paragraph:
    title: str
    number: int
    points: list[Point]


@dataclass
class Chapter:
    title: str
    number: int
    paragraphs: list[Paragraph]


@dataclass
class Document:
    title: str
    chapters: list[Chapter]
