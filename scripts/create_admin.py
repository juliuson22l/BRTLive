"""
Script to create an admin user for BRTLive system.
Run this script to create your first admin user.

Usage:
    python scripts/create_admin.py
    
Or with custom details:
    python scripts/create_admin.py --username admin --email admin@brtlive.com
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def create_admin_user(
    username: str = "admin",
    email: str = "admin@brtlive.com",
    password: str = "brtadmin123",
    full_name: str = "System Administrator"
):
    """Create an admin user"""
    
    # Create async engine
    engine = create_async_engine(settings.db_url, echo=True)
    AsyncSessionLocal = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if user already exists
            query = select(User).where(User.username == username)
            result = await session.execute(query)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                print(f"❌ User '{username}' already exists!")
                return False
            
            # Check if email already exists
            email_query = select(User).where(User.email == email)
            email_result = await session.execute(email_query)
            existing_email = email_result.scalar_one_or_none()
            
            if existing_email:
                print(f"❌ Email '{email}' already in use!")
                return False
            
            # Create admin user
            hashed_password = get_password_hash(password)
            admin_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                full_name=full_name,
                role=UserRole.ADMIN,
                is_active=True
            )
            
            session.add(admin_user)
            await session.commit()
            await session.refresh(admin_user)
            
            print("\n" + "="*50)
            print("✅ Admin user created successfully!")
            print("="*50)
            print(f"👤 Username: {username}")
            print(f"📧 Email: {email}")
            print(f"🔑 Password: {password}")
            print(f"👑 Role: {admin_user.role.value}")
            print(f"🆔 User ID: {admin_user.id}")
            print("="*50)
            print("\n⚠️  IMPORTANT: Change the password after first login!")
            print(f"Login at: http://localhost:8000/docs (Swagger UI)")
            print("="*50 + "\n")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            await session.rollback()
            return False
        finally:
            await engine.dispose()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create an admin user for BRTLive system.")
    parser.add_argument("--username", type=str, default="admin", help="Admin username")
    parser.add_argument("--email", type=str, default="admin@brtlive.com", help="Admin email")
    parser.add_argument("--password", type=str, default="admin123", help="Admin password")
    parser.add_argument("--full_name", type=str, default="System Administrator", help="Admin full name")
    args = parser.parse_args()

    asyncio.run(create_admin_user(
        username=args.username,
        email=args.email,
        password=args.password,
        full_name=args.full_name
    ))

