from pydantic import BaseModel, RootModel


class Texts(RootModel[list[str]]):
    pass


class Embeddings(RootModel[list[list[float]]]):
    pass


class DocumentWithTokens(BaseModel):
    label: str
    text: str
    tokens_number: int
