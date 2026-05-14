from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import backend.app.models  # noqa: F401
from backend.app.core.security import hash_password
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import create_app
from backend.app.models.company import Company
from backend.app.models.enums import UserRole
from backend.app.models.sector import Sector
from backend.app.models.user import User


@pytest.fixture
def db_session() -> Generator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db_session

    app = create_app()
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def company(db_session: Session) -> Company:
    company_record = Company(name="PRO CORE Test")
    db_session.add(company_record)
    db_session.commit()
    db_session.refresh(company_record)
    return company_record


def create_user(
    db: Session,
    company: Company,
    role: UserRole,
    email: str,
    full_name: str,
    sector: Sector | None = None,
) -> User:
    user = User(
        company_id=company.id,
        sector_id=sector.id if sector else None,
        full_name=full_name,
        email=email,
        password_hash=hash_password("OldPassword123"),
        role=role,
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session: Session, company: Company) -> User:
    return create_user(
        db=db_session,
        company=company,
        role=UserRole.ADMIN,
        email="admin@example.com",
        full_name="Admin Test",
    )


@pytest.fixture
def technician_user(db_session: Session, company: Company) -> User:
    return create_user(
        db=db_session,
        company=company,
        role=UserRole.TECHNICIAN,
        email="tech@example.com",
        full_name="Technician Test",
    )


@pytest.fixture
def auth_headers(client: TestClient, admin_user: User) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": admin_user.email, "password": "OldPassword123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
