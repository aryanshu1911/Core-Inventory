import asyncio
from sqlalchemy import select
from database import AsyncSessionLocal
from models.user import User

async def list_users():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        if not users:
            print("No users found in database.")
        for u in users:
            print(f"User: {u.email} (Role: {u.role})")

if __name__ == "__main__":
    asyncio.run(list_users())
