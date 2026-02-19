class FileNameExist(Exception):
    def __init__(self, filename: str):
        self.file_name = filename


class EmptyFileException(Exception):
    def __init__(self, filename: str):
        self.file_name = filename


class ObjectExists(Exception):
    pass


class FileNameNotProvided(Exception):
    pass
