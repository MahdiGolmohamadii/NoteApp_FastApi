from passlib.context import CryptContext

from .config import settings



pwd_context = CryptContext(schemes=["bcrypt"])


def get_passwords_hashed(password: str):
    return pwd_context.hash(password)
