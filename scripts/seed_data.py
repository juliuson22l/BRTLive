import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings
from app.models import User, Terminal, Bus, Driver
from app.models.user import UserRole
from app.core.security import get_password_hash


async def seed_database():
    """Seed database with sample data"""
    
    # Create async engine
    engine = create_async_engine(settings.ASYNC_DATABASE_URL, echo=True)
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        try:
            print("\n🌱 Seeding database with sample data...\n")
            
            # Create sample users
            print("👥 Creating users...")
            users = [
                User(
                    username="admin",
                    email="admin@brtlive.com",
                    hashed_password=get_password_hash("brtadmin123"),
                    full_name="System Administrator",
                    role=UserRole.ADMIN
                ),
                User(
                    username="driver1",
                    email="driver1@brtlive.com",
                    hashed_password=get_password_hash("driver123"),
                    full_name="John Driver",
                    role=UserRole.DRIVER
                ),
                User(
                    username="viewer1",
                    email="viewer1@brtlive.com",
                    hashed_password=get_password_hash("viewer123"),
                    full_name="Jane Viewer",
                    role=UserRole.VIEWER
                ),
                User(
                    username="Julius",
                    email="julius@brtlive.com",
                    hashed_password=get_password_hash("julius123"),
                    full_name="Julius Ali",
                    role=UserRole.DRIVER
                ),
                User(
                    username="Chioma",
                    email="chioma@brtlive.com",
                    hashed_password=get_password_hash("chioma123"),
                    full_name="Chioma Okafor",
                    role=UserRole.DRIVER
                ),
                User(
                    username="Adebayo",
                    email="adebayo@brtlive.com",
                    hashed_password=get_password_hash("adebayo123"),
                    full_name="Adebayo Williams",
                    role=UserRole.DRIVER
                ),
                User(
                    username="Tomine",
                    email="tomine@brtlive.com",
                    hashed_password=get_password_hash("tomine123"),
                    full_name="Tomine Eze",
                    role=UserRole.DRIVER
                ),
                User(
                    username="Prosper",
                    email="prosper@brtlive.com",
                    hashed_password=get_password_hash("prosper123"),
                    full_name="Prosper Hassan",
                    role=UserRole.DRIVER
                ),
            ]
            
            for user in users:
                session.add(user)
            
            # Create sample terminals
            print("🏢 Creating terminals...")
            terminals = [
                Terminal(
                    name="Ikorodu Terminal",
                    address="Ikorodu Road, Lagos",
                    latitude=6.6170,
                    longitude=3.5042,
                    capacity=25
                ),
                Terminal(
                    name="Berger Terminal",
                    address="Berger Bus Stop, Lagos",
                    latitude=6.5698,
                    longitude=3.3660,
                    capacity=30
                ),
                Terminal(
                    name="Obalende Terminal",
                    address="Obalende, Lagos Island",
                    latitude=6.4420,
                    longitude=3.4106,
                    capacity=20
                ),
                Terminal(
                    name="CMS Terminal",
                    address="Central Business District, Lagos",
                    latitude=6.4531,
                    longitude=3.3958,
                    capacity=35
                )
            ]
            
            for terminal in terminals:
                session.add(terminal)
            
            await session.commit()
            
            # Create sample drivers
            print("👨‍✈️ Creating drivers...")
            drivers = [
                Driver(
                    name="Julius Ali",
                    phone_number="+2348142388316",
                    user_id=users[3].id,
                    license_number="LAG-DRIVER-001"
                ),
                Driver(
                    name="Chioma Okafor",
                    phone_number="+2348149927828",
                    user_id=users[4].id,
                    license_number="LAG-DRIVER-002"
                ),
                Driver(
                    name="Adebayo Williams",
                    phone_number="+2347032397424",
                    user_id=users[5].id,
                    license_number="LAG-DRIVER-003"
                ),
                Driver(
                    name="Tomine Eze",
                    phone_number="+2347035130806",
                    user_id=users[6].id,
                    license_number="LAG-DRIVER-004"
                ),
                Driver(
                    name="Prosper Hassan",
                    phone_number="+2348108730674",
                    user_id=users[7].id,
                    license_number="LAG-DRIVER-005"
                )
            ]
            
            for driver in drivers:
                session.add(driver)
            
            await session.commit()
            
            # Create sample buses
            print("🚌 Creating buses...")
            buses = [
                Bus(
                    plate_number="LAG-123-XY",
                    capacity=40,
                    current_terminal_id=terminals[0].id,
                    latitude=6.6170,
                    longitude=3.5042,
                    is_active=True
                ),
                Bus(
                    plate_number="LAG-456-AB",
                    capacity=45,
                    current_terminal_id=terminals[1].id,
                    latitude=6.5698,
                    longitude=3.3660,
                    is_active=True
                ),
                Bus(
                    plate_number="LAG-789-CD",
                    capacity=40,
                    current_terminal_id=terminals[2].id,
                    latitude=6.4420,
                    longitude=3.4106,
                    is_active=True
                ),
                Bus(
                    plate_number="LAG-012-EF",
                    capacity=50,
                    current_terminal_id=terminals[3].id,
                    latitude=6.6170,
                    longitude=3.5042,
                    is_active=True
                ),
                Bus(
                    plate_number="LAG-345-GH",
                    capacity=55,
                    current_terminal_id=terminals[1].id,
                    latitude=6.6170,
                    longitude=3.5042,
                    is_active=True
                )
            ]
            
            for bus in buses:
                session.add(bus)
            
            await session.commit()
            
            print("\n" + "="*50)
            print("✅ Database seeded successfully!")
            print("="*50)
            print(f"👥 Users created: {len(users)}")
            print(f"🏢 Terminals created: {len(terminals)}")
            print(f"👨‍✈️ Drivers created: {len(drivers)}")
            print(f"🚌 Buses created: {len(buses)}")
            print("="*50)
            print("\n📝 Login Credentials:")
            print("="*50)
            print("Admin:")
            print("  Username: admin")
            print("  Password: brtadmin123")
            print("\nDriver:")
            print("  Username: driver1")
            print("  Password: driver123")
            print("\nViewer:")
            print("  Username: viewer1")
            print("  Password: viewer123")
            print("="*50 + "\n")
            
        except Exception as e:
            print(f"❌ Error seeding database: {e}")
            await session.rollback()
        finally:
            await engine.dispose()


def main():
    """Main function"""
    asyncio.run(seed_database())


if __name__ == "__main__":
    main()