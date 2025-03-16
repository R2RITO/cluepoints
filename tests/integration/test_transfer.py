import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from main import app, get_db
from models.account import Account, AccountType
from models.user import User

# In-memory SQLite database for testing
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_db_override():
        yield session

    app.dependency_overrides[get_db] = get_db_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_integration_create_user_account_transfer(client: TestClient, session: Session):
    # 1. Create a user
    user_data = {
        "first_name": "Integration",
        "last_name": "Test",
        "date_of_birth": "1985-01-01",
        "street": "1600 Amphitheatre Parkway",
        "city": "Mountain View",
        "postal_code": "94043",
        "country": "USA",
    }
    user_response = client.post("/users/", json=user_data)
    assert user_response.status_code == 201
    user_data_response = user_response.json()
    user_id = user_data_response["id"]

    # 2. Verify user in the database
    db_user = session.get(User, user_id)
    assert db_user is not None
    assert db_user.first_name == "Integration"
    assert db_user.latitude is not None
    assert db_user.longitude is not None

    # 3. Create account types directly in the database
    account_type1 = AccountType(name="Savings")
    account_type2 = AccountType(name="Checking")
    session.add(account_type1)
    session.add(account_type2)
    session.commit()

    # 4. Create an account
    account_data = {
        "account_number": "123456789",
        "balance": 1000.0,
        "account_type_id": account_type1.id,
        "user_id": user_id,
    }

    account_response = client.post("/accounts/", json=account_data)
    assert account_response.status_code == 201
    account_data_response = account_response.json()
    account_id = account_data_response["id"]

    # 5. Create a second account
    second_account_data = {
        "account_number": "987654321",
        "balance": 500.0,
        "account_type_id": account_type2.id,
        "user_id": user_id,
    }
    second_account_response = client.post("/accounts/", json=second_account_data)
    assert second_account_response.status_code == 201
    second_account_data_response = second_account_response.json()
    second_account_id = second_account_data_response["id"]

    # 6. Transfer funds
    transfer_data = {
        "from_account_id": account_id,
        "to_account_id": second_account_id,
        "amount": 500.0,
    }
    transfer_response = client.post("/accounts/transfer/", json=transfer_data)
    assert transfer_response.status_code == 200

    # 7. Verify balances in the database
    updated_account = session.get(Account, account_id)
    updated_second_account = session.get(Account, second_account_id)
    assert updated_account.balance == 500.0
    assert updated_second_account.balance == 1000.0
