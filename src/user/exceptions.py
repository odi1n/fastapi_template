from fastapi import HTTPException


class UserEmailExistsError(Exception):
    def __init__(self, email: str):
        self.email = email


credentials_exception = HTTPException(
    status_code=401,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
