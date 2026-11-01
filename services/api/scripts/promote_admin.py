"""Promote an existing account to admin. Run only from a trusted operator shell."""
import asyncio
import sys
from sqlalchemy import select
from app.db.session import SessionLocal, engine
from app.models.user import User

async def main():
    if len(sys.argv) != 2 or "@" not in sys.argv[1]:
        raise SystemExit("Usage: python scripts/promote_admin.py account@example.com")
    email = sys.argv[1].strip().lower()
    async with SessionLocal() as db:
        user = await db.scalar(select(User).where(User.email == email))
        if user is None:
            raise SystemExit("Account not found; create and verify the account first.")
        user.role = "admin"
        await db.commit()
        print(f"Promoted {email} to admin.")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
