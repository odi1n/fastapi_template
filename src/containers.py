from dependency_injector import containers, providers

from src.database import Database
from src.user.private.repositories import UserRepository
from src.user.services import UserService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["src"], auto_wire=True)
    config = providers.Configuration()

    db = providers.Singleton(Database, db_url=config.DB_DSN)

    user_repository = providers.Factory(
        UserRepository, session_factory=db.provided.get_session
    )
    user_service = providers.Factory(UserService, repository=user_repository)
