import asyncio
import random

from faker import Faker

from app.db import AsyncSessionLocal, Base, engine
from app.models import Property

fake = Faker()
CITIES = ["Bangalore", "Mumbai", "Delhi", "Hyderabad", "Chennai"]
STATES = {
    "Bangalore": "Karnataka",
    "Mumbai": "Maharashtra",
    "Delhi": "Delhi",
    "Hyderabad": "Telangana",
    "Chennai": "Tamil Nadu",
}
COUNTRY = "India"


async def seed_properties(n=50):
    async with AsyncSessionLocal() as session:
        for _ in range(n):
            city = random.choice(CITIES)
            state = STATES[city]
            prop = Property(
                no_of_bedrooms=random.randint(1, 5),
                no_of_bathrooms=random.randint(1, 3),
                carpet_area=random.randint(300, 1200),
                total_area=random.randint(400, 1500),
                country=COUNTRY,
                state=state,
                city=city,
                community=fake.word().capitalize() + " Community",
                building_name=fake.company() + " Tower",
                asking_price=random.randint(3000000, 15000000),
            )
            session.add(prop)
        await session.commit()
    print(f"Seeded {n} properties.")


async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await seed_properties()


if __name__ == "__main__":
    asyncio.run(init())
