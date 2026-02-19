class UserExists(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class UserNotFound(Exception):
    pass


class UserCantLog(Exception):
    pass


class VectorCollectionNotFound(Exception):
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
