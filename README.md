# FastApi Template

## Git
Используется GitFlow подход.

Желательно в проекте не делать прямых изменений в ветках(main, dev, stage).

Если коммит не является важным, и не несет существенной нагрузки, делать его в ветках(main, dev, stage) - нежелательно

### Naming branch
Ветки именовать следующим образом: `dev/NAMING`:
- `dev` - указывает на то что ветка была сделана в develop среде
- `NAMING` - номер задачи

#### Правило
Для нейминга веток, лучше придерживаться правила: `Convential Commit`:
- Для продуктов JetBrains, можно использовать plugin `Convential Commit`

## Runing
### Local
1. `pre-commit install` - включить при git pull;
2. `python src/__main__.py`

### Docker
1. `docker-compose up --build`

### Prod
1. `docker-compose -f docker-compos.prod.yml --build -d`

## Архитектура

### Ознакомление
1. [Видео](https://youtu.be/8Im74b55vFc)
2. [Видео - как делать transaction](https://www.youtube.com/watch?v=TaYg23VkCRI)
3. [Пример подобной структуры проекта](https://github.com/zhanymkanov/fastapi-best-practices/blob/master/README.md)

### Описание текущей
В текущем проекте выбран подход Многослойной(луковичной, слоистая) архитектуры.
```
familia
├── _docker                      # docker configuration
│   └── web
│   │    ├── Dockerfile          # local
│   │    └── Dockerfile.prod     # prod
├── alembic                      # alembic settings, migrations
│   ├── versions
│   │   └── 000001.py
│   ├── env.py
├── src
│   ├── common                    # global directory
│   │   ├── constants.py          # local constants
│   │   ├── excetions.py           # global
│   │   ├── interfaces.py         # global
│   │   ├── mixins.py             # global
│   │   ├── repositories.py       # global
│   │   └── schemas.py            # global
│   ├── user
│   │   ├── private
│   │   │   ├── models.py         # db model
│   │   │   └── repositories.py   # interaction with the database
│   │   ├── web
│   │   │   └── rest.py           # local routers
│   │   ├── constants.py          # local constants
│   │   ├── eceptions.py          # local exception
│   │   ├── interface.py          # local interface repository and service
│   │   ├── schemas.py            # schema for model
│   │   └── services.py           # local services
│   ├── utils                     # additional functionality
│   │   └── export.py
│   ├── __main__.py               # run application
│   ├── app.py                    # create application
│   ├── containers.py             # di container
│   ├── routes.py                 # set all routes
│   ├── server.py                 # setting for fastapi
│   └── setting.py                # settings for project
├── tests
├── env.example
├── .gitignore
├── alembic.ini
├── .pre-commit-confio.yaml       # pre-commit config
├── docker-compose.prod.yml       # production
├── docker-compose.yml            # local
├── pyproject.toml                # all libs
├── README.md
└── setup.cfg                     # flake8, mypy config
```
1. Хранить все каталоги домена внутри srcпапки
    - `src/`- самый высокий уровень приложения, содержит общие модели, конфигурации, константы и т. д.
    - `src/app.py` - корень проекта, который инициализирует приложение FastAPI
2. Модули:
   - `common` - содержит базовый функционал, все последующие модули его наследуют
   - `user` - содержит специфичный функционал для работы с пользователем
3. Каждый пакет имеет свой маршрутизатор, схемы, модели и т. д.
    - `exceptions.py` - исключения, специфичные для модуля, например PostNotFound,InvalidUserData
    - `interface.py` - описывается схема для repositories, service и другого
    - `mixins.py` - миксины специфичные для модуля
    - `repositories.py` - реализация работы с БД специфичные для модуля
    - `schemas.py` - для pydantic моделей
    - `models.py` - для моделей БД
    - `rest.py` - является ядром каждого модуля со всеми конечными точками
    - `service.py` - бизнес-логика, специфичная для модуля
    - `constants.py` - специфичные для модуля константы и коды ошибок
    - `service.py` - специфичная для модуля бизнес логика
    - `utils.py` - функции, не относящиеся к бизнес-логике, например, нормализация ответов, обогащение данных и т. д.
    - `app.py` - инициализация приложения
    - `containers.py` - di container
    - `routers.py` - содержит класс инициализации всех роутов
    - `server.py` - настройка приложени. подключение роутов, мидлвар и тд.
    - `settings.py` - настройки, переменные окружения и тд.
4. Если пакету требуются службы, зависимости или константы из других пакетов — импортируйте их с явным именем модуля.
```python
from src.auth import constants as auth_constants
from src.notifications import service as notification_service
from src.posts.constants import ErrorCode as PostsErrorCode  # in case we have Standard ErrorCode in constants module of each package
```