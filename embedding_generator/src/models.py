from pydantic import RootModel


class Texts(RootModel[list[str]]):
    pass


class Embeddings(RootModel[list[list[float]]]):
    pass
