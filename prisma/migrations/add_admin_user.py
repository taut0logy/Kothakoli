import asyncio
import bcrypt
import uuid
from datetime import datetime
from prisma import Prisma

async def main():
    db = Prisma()
    await db.connect()

    # Hash the password
    password = "admin123"  # Replace with your desired password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode(), salt)

    # Create or update admin user
    admin = await db.user.upsert(
        where={
            "email": "admin@kothakoli.ai"  # Replace with your admin email
        },
        data={
            "create": {
                "email": "admin@kothakoli.ai",
                "password": hashed_password.decode(),
                "name": "Admin",
                "role": "ADMIN",
                "isVerified": True,
                "emailVerified": True,
                "verifiedAt": datetime.now(),
                "apiKey": str(uuid.uuid4()),
                "modelName": "gemini-2.0-flash-exp"
            },
            "update": {}
        }
    )

    print("Admin user created:", admin)
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main()) 