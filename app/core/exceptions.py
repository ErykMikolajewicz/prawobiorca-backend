

class UserExists(Exception):
    def __init__(self, message="User with that login already exists!"):
        self.message = message
        super().__init__(self.message)


class NoFileName(Exception):
    pass


class FileNameExist(Exception):
    pass
