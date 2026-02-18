class VectorCollectionNotFound(Exception):
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
