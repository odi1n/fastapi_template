from dependency_injector import containers, providers

from src.database import Database
from src.user.private.repositories import UserRepository
from src.user.services import UserService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    db = providers.Singleton(Database)

    user_repository = providers.Factory(UserRepository, session=db.provided.get_session)
    user_service = providers.Factory(UserService, repository=user_repository)
