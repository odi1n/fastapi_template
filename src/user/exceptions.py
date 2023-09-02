class UserEmailExistsError(Exception):
    def __init__(self, email: str):
        self.email = email
