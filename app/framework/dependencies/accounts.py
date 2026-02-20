from app.application.use_cases.account import CreateAccount


def create_account_provider() -> type[CreateAccount]:
    return CreateAccount
