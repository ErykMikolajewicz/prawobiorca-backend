class UserExists(Exception):
    pass


class FileNameExist(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class UserNotFound(Exception):
    pass


class EmptyFileException(Exception):
    pass


class RelationalDbIntegrityError(Exception):
    pass


class UserCantLog(Exception):
    pass
