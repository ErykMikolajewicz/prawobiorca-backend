class UserExists(Exception):
    pass


class FileNameExist(Exception):
    def __init__(self, filename: str):
        self.file_name = filename


class InvalidCredentials(Exception):
    pass


class UserNotFound(Exception):
    pass


class EmptyFileException(Exception):
    def __init__(self, filename: str):
        self.file_name = filename


class RelationalDbIntegrityError(Exception):
    pass


class UserCantLog(Exception):
    pass


class FileNameNotProvided(Exception):
    pass
