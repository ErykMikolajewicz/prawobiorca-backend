class UserExists(Exception):
    pass


class UserCantLog(Exception):
    pass


class RegulationsNotPreparedToSearch(Exception):
    def __init__(self, regulations_name: str):
        self.regulations_name = regulations_name


class FileNameExist(Exception):
    def __init__(self, filename: str):
        self.file_name = filename


class FileNameTooLong(Exception):
    def __init__(self, filename: str):
        self.file_name = filename


class InvalidCharacterInFileName(Exception):
    def __init__(self, filename: str):
        self.file_name = filename


class RegulationAlreadyInitialized(Exception):
    pass
