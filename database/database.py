from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from configs import config

TORTOISE_ORM = {
    "connections": {
        "default": config.database_connections,
    },
    "apps": {
        "models": {
            "models":["database.model", "aerich.models"],
            "default_connection": "default",
        },
    },
}

def init_db(app: FastAPI) -> None:
    register_tortoise(
        app,
        db_url=config.database_connections,
        modules={"models": [
            "database.model"
        ]},
        generate_schemas=True,
        add_exception_handlers=True,
    )
