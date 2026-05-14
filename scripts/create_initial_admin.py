from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select  # noqa: E402
from sqlalchemy.exc import SQLAlchemyError  # noqa: E402

from backend.app.core.security import hash_password  # noqa: E402
from backend.app.db.session import SessionLocal  # noqa: E402
from backend.app.models.company import Company  # noqa: E402
from backend.app.models.enums import UserRole  # noqa: E402
from backend.app.models.user import User  # noqa: E402
from backend.app.services.users import normalize_email  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create the initial PRO CORE administrator.")
    parser.add_argument("--company-name", required=True)
    parser.add_argument("--admin-name", required=True)
    parser.add_argument("--email", required=True)
    parser.add_argument("--password", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    email = normalize_email(args.email)

    with SessionLocal() as db:
        try:
            existing_user = db.scalars(select(User).where(User.email == email)).first()
            if existing_user is not None:
                print(f"User already exists: {email}")
                return 1

            company = db.scalars(
                select(Company).where(Company.name == args.company_name.strip())
            ).first()
            if company is None:
                company = Company(name=args.company_name.strip())
                db.add(company)
                db.flush()

            admin = User(
                company_id=company.id,
                full_name=args.admin_name.strip(),
                email=email,
                password_hash=hash_password(args.password),
                role=UserRole.ADMIN,
                must_change_password=True,
            )
            db.add(admin)
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            print(f"Failed to create initial admin: {exc}")
            return 1

    print(f"Initial admin created: {email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
