class UserExists(Exception):
    pass


class UserCantLog(Exception):
    pass


class RegulationsNotPreparedToSearch(Exception):
    def __init__(self, regulations_name: str):
        self.regulations_name = regulations_name


class RegulationAlreadyInitialized(Exception):
    pass


class ToLongHeaderSection(Exception):
    pass


class ToLongDocument(Exception):
    pass


class CaseNotFound(Exception):
    pass
