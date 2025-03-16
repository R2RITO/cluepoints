# FastAPI User and Account Management API

This project provides a REST API for managing users and their accounts, built with FastAPI, SQLModel, and PostgreSQL.

## Features

* **User Management:**
    * Create, read, update, and delete users.
    * Geocoding of user addresses (calculating latitude and longitude).
* **Account Management:**
    * Create, read, and perform transfers between accounts.
    * Account types with relationships.
    * Database-level constraints to prevent negative balances.
    * Atomic fund transfers with database locking to prevent race conditions.
* **Testing:**
    * Comprehensive unit and integration tests with pytest.
* **Code Quality:**
    * Automated code formatting with Black.
    * Import sorting with isort.
    * Linting with Ruff.
    * Automated code checks with pre-commit.
* **Dependency Management:**
    * Poetry for dependency management and virtual environments.

## Prerequisites

* Python 3.8+
* PostgreSQL database
* Poetry

## Installation

1.  **Install Poetry:**

    ```bash
    curl -sSL [https://install.python-poetry.org](https://install.python-poetry.org) | python3 -
    ```

2.  **Clone the repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

3.  **Install dependencies using Poetry:**

    ```bash
    poetry install
    ```

4.  **Configure PostgreSQL:**

    * Create a PostgreSQL database.
    * Export the environment variables DB_USERNAME, DB_PASSWORD and DB_HOST

5.  **Install pre-commit hooks:**

    ```bash
    poetry run pre-commit install
    ```

## Running the Application

1.  **Start the FastAPI application:**

    ```bash
    poetry run uvicorn main:app --reload
    ```

2.  **Access the API:**

    * The API will be available at `http://127.0.0.1:8000`.
    * API documentation (Swagger UI) is available at `http://127.0.0.1:8000/docs`.

## Running Tests

* **Run all tests:**

    ```bash
    poetry run python -m pytest
    ```

## Code Quality

* **Run pre-commit checks manually:**

    ```bash
    poetry run pre-commit run --all-files
    ```

## Project Structure

cluepoints/
├── database/
│   └── postgres.py     # Database configuration
├── models/            # SQLModel models
│   ├── user.py
│   └── account.py
├── tests/
│   ├── integration/
│   │   └── test_transfer.py
│   ├── unit/
│   └──  └── test_main.py        # Unit and integration tests
├── main.py             # FastAPI application
├── pyproject.toml         # Poetry configuration
├── poetry.lock            # Poetry lock file
├── .pre-commit-config.yaml # pre-commit configuration
└── ruff.toml               # Ruff configuration.