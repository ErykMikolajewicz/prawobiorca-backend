import asyncio
import sys

sys.path.append(".")

from sqlalchemy import insert

from app.infrastructure.relational_db.connection import async_session_maker
from app.infrastructure.relational_db.schemas.users import Users


async def seed_db():
    session = async_session_maker()

    # password is PrawobiorcaPassword1;
    statement = insert(Users).values(
        username="PrawobiorcaTester", hashed_password=b"$2b$12$NY0/W4kDgXcfQteV/gnsGeqvqGUaNiy/1K/NXAov0kbpEUAPNWRVG"
    )

    await session.execute(statement)
    await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_db())
