import asyncio

from sqlalchemy import select

from app.core.db import async_session_maker
from app.models import Activity, Building, Organization, organization_activity


async def seed() -> None:
    async with async_session_maker() as session:
        existing = (await session.execute(select(Building.id).limit(1))).first()
        if existing:
            print("Database already seeded, skipping.")
            return

        # Activities (3 levels)
        food = Activity(name="Еда")
        meat = Activity(name="Мясная продукция", parent=food)
        sausages = Activity(name="Колбасы", parent=meat)
        dairy = Activity(name="Молочная продукция", parent=food)

        cars = Activity(name="Автомобили")
        trucks = Activity(name="Грузовые", parent=cars)
        passenger = Activity(name="Легковые", parent=cars)
        parts = Activity(name="Запчасти", parent=passenger)
        accessories = Activity(name="Аксессуары", parent=cars)

        all_activities = [food, meat, sausages, dairy, cars, trucks, passenger, parts, accessories]
        for act in all_activities:
            if act.depth() > Activity.MAX_DEPTH:
                raise ValueError(f"Activity '{act.name}' exceeds max depth {Activity.MAX_DEPTH}")
        session.add_all(all_activities)

        # Buildings (Krasnoyarsk)
        b1 = Building(address="ул. Ленина, 1", latitude=56.0097, longitude=92.8526)
        b2 = Building(address="ул. Мира, 10", latitude=56.0087, longitude=92.8700)
        b3 = Building(address="ул. Блюхера, 32/1", latitude=56.0200, longitude=92.8400)
        b4 = Building(address="пр. Свободный, 75", latitude=56.0500, longitude=92.9000)

        session.add_all([b1, b2, b3, b4])

        # Flush to get IDs for M2M
        await session.flush()

        # Organizations
        org1 = Organization(
            name='ООО "Рога и Копыта"',
            building=b1,
            phones=["2-222-222", "3-333-333"],
        )
        org2 = Organization(
            name='ООО "Молочный край"',
            building=b1,
            phones=["8-923-666-13-13"],
        )
        org3 = Organization(
            name='ООО "Автосервис Плюс"',
            building=b2,
            phones=["4-444-444"],
        )
        org4 = Organization(
            name='ООО "Рога и Ко"',
            building=b3,
            phones=["5-555-555"],
        )
        org5 = Organization(
            name='ООО "ГрузовикТорг"',
            building=b4,
            phones=["6-666-666"],
        )

        session.add_all([org1, org2, org3, org4, org5])
        await session.flush()

        # M2M: organization <-> activity
        await session.execute(
            organization_activity.insert(),
            [
                {"organization_id": org1.id, "activity_id": meat.id},
                {"organization_id": org2.id, "activity_id": dairy.id},
                {"organization_id": org3.id, "activity_id": parts.id},
                {"organization_id": org3.id, "activity_id": accessories.id},
                {"organization_id": org4.id, "activity_id": food.id},
                {"organization_id": org5.id, "activity_id": trucks.id},
            ],
        )

        await session.commit()
        print("Seed data inserted successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
