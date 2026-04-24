from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.api.source_routes import get_current_user
from app.database.database import Base, get_db
from app.database import models


SQLALCHEMY_TEST_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class _CurrentUser:
    id = 0


CURRENT_USER = _CurrentUser()


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return CURRENT_USER


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_list_sources_only_returns_current_users_sources():
    db = TestingSessionLocal()
    owner = models.User(email="owner@example.com", hashed_password="pw")
    other_user = models.User(email="other@example.com", hashed_password="pw")
    db.add_all([owner, other_user])
    db.commit()
    db.refresh(owner)
    db.refresh(other_user)

    db.add_all(
        [
            models.ContentSource(
                user_id=owner.id,
                source_type="rss",
                source_url="https://owner.example/rss",
                name="Owner Feed",
            ),
            models.ContentSource(
                user_id=other_user.id,
                source_type="rss",
                source_url="https://other.example/rss",
                name="Other Feed",
            ),
        ]
    )
    db.commit()
    db.close()

    CURRENT_USER.id = owner.id
    response = client.get("/api/sources")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Owner Feed"
    assert payload[0]["source_url"] == "https://owner.example/rss"
    assert payload[0]["user_id"] == owner.id


def test_list_sources_response_shape_matches_frontend_usage():
    db = TestingSessionLocal()
    user = models.User(email="shape@example.com", hashed_password="pw")
    db.add(user)
    db.commit()
    db.refresh(user)

    source = models.ContentSource(
        user_id=user.id,
        source_type="rss",
        source_url="https://shape.example/rss",
        name="Shape Feed",
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    db.close()

    CURRENT_USER.id = user.id
    response = client.get("/api/sources")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert set(payload[0].keys()) == {
        "id",
        "user_id",
        "source_type",
        "source_url",
        "name",
        "last_fetched_at",
        "created_at",
    }
    assert payload[0]["id"] == source.id
    assert payload[0]["user_id"] == user.id
    assert payload[0]["source_type"] == "rss"
    assert payload[0]["source_url"] == "https://shape.example/rss"
    assert payload[0]["name"] == "Shape Feed"
    assert payload[0]["last_fetched_at"] is None
    assert payload[0]["created_at"]
