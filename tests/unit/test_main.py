import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from main import app, get_db
from models.account import Account, AccountCreate, AccountType
from models.user import User, UserCreate

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


def test_create_user(client: TestClient):
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "street": "123 Main St",
        "city": "Anytown",
        "postal_code": "12345",
        "country": "USA",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert "id" in data


def test_list_users(client: TestClient, session: Session):
    user_data = UserCreate(
        first_name="Jane",
        last_name="Smith",
        date_of_birth="1995-05-05",
        street="456 Elm St",
        city="Othertown",
        postal_code="67890",
        country="Canada",
    )
    db_user = User.model_validate(user_data)
    session.add(db_user)
    session.commit()
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["first_name"] == "Jane"


def test_update_user(client: TestClient, session: Session):
    user_data = UserCreate(
        first_name="Alice",
        last_name="Johnson",
        date_of_birth="1985-10-10",
        street="789 Oak Ave",
        city="Somecity",
        postal_code="13579",
        country="UK",
    )
    db_user = User.model_validate(user_data)
    session.add(db_user)
    session.commit()
    updated_data = {
        "first_name": "Bob",
        "last_name": "Johnson",
        "date_of_birth": "1985-10-10",
        "street": "789 Oak Ave",
        "city": "Somecity",
        "postal_code": "13579",
        "country": "UK",
    }
    response = client.put(f"/users/{db_user.id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Bob"


def test_get_user(client: TestClient, session: Session):
    user_data = UserCreate(
        first_name="Charlie",
        last_name="Brown",
        date_of_birth="2000-12-12",
        street="101 Pine Ln",
        city="Anothercity",
        postal_code="24680",
        country="Australia",
    )
    db_user = User.model_validate(user_data)
    session.add(db_user)
    session.commit()
    response = client.get(f"/users/{db_user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Charlie"


def test_create_account(client: TestClient, session: Session):
    user_data = UserCreate(
        first_name="David",
        last_name="Williams",
        date_of_birth="1975-03-15",
        street="111 Cedar Rd",
        city="Yetanothercity",
        postal_code="98765",
        country="Germany",
    )
    db_user = User.model_validate(user_data)
    session.add(db_user)
    session.commit()

    account_type_data = AccountType(name="Savings")
    session.add(account_type_data)
    session.commit()

    account_data = {
        "account_number": "1234567890",
        "balance": 1000.0,
        "account_type_id": account_type_data.id,
        "user_id": db_user.id,
    }
    response = client.post("/accounts/", json=account_data)
    assert response.status_code == 201
    data = response.json()
    assert data["account_number"] == "1234567890"


def test_transfer_funds(client: TestClient, session: Session):
    user_data = UserCreate(
        first_name="Eve",
        last_name="Davis",
        date_of_birth="1980-08-20",
        street="222 Birch St",
        city="Finalcity",
        postal_code="54321",
        country="France",
    )
    db_user = User.model_validate(user_data)
    session.add(db_user)
    session.commit()

    account_type_data = AccountType(name="Checking")
    session.add(account_type_data)
    session.commit()

    from_account_data = AccountCreate(
        account_number="1111222233",
        balance=1000.0,
        account_type_id=account_type_data.id,
        user_id=db_user.id,
    )
    to_account_data = AccountCreate(
        account_number="4444555566",
        balance=500.0,
        account_type_id=account_type_data.id,
        user_id=db_user.id,
    )
    from_account = Account.model_validate(from_account_data)
    to_account = Account.model_validate(to_account_data)
    session.add(from_account)
    session.add(to_account)
    session.commit()

    transfer_data = {
        "from_account_id": from_account.id,
        "to_account_id": to_account.id,
        "amount": 500.0,
    }
    response = client.post("/accounts/transfer/", json=transfer_data)
    assert response.status_code == 200

    updated_from_account = session.get(Account, from_account.id)
    updated_to_account = session.get(Account, to_account.id)
    assert updated_from_account.balance == 500.0
    assert updated_to_account.balance == 1000.0


def test_transfer_insufficient_funds(client: TestClient, session: Session):
    user_data = UserCreate(
        first_name="Insufficient",
        last_name="Funds",
        date_of_birth="1990-01-01",
        street="123 Insufficient St",
        city="Nowhere",
        postal_code="00000",
        country="Testland",
    )
    db_user = User.model_validate(user_data)
    session.add(db_user)
    session.commit()

    account_type_data = AccountType(name="InsufficientFundsAccountType")
    session.add(account_type_data)
    session.commit()

    from_account_data = AccountCreate(
        account_number="123456789",
        balance=100.0,
        account_type_id=account_type_data.id,
        user_id=db_user.id,
    )
    to_account_data = AccountCreate(
        account_number="987654321",
        balance=500.0,
        account_type_id=account_type_data.id,
        user_id=db_user.id,
    )
    from_account = Account.model_validate(from_account_data)
    to_account = Account.model_validate(to_account_data)
    session.add(from_account)
    session.add(to_account)
    session.commit()

    transfer_data = {
        "from_account_id": from_account.id,
        "to_account_id": to_account.id,
        "amount": 200.0,  # Attempt to transfer more than the balance
    }
    response = client.post("/accounts/transfer/", json=transfer_data)
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Insufficient funds"

    # Verify that balances are unchanged
    updated_from_account = session.get(Account, from_account.id)
    updated_to_account = session.get(Account, to_account.id)
    assert updated_from_account.balance == 100.0
    assert updated_to_account.balance == 500.0
