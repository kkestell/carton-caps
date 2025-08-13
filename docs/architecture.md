# Architecture Overview

This project is intended as a coding exercise/demonstration, and aims to strike a balance between a bare-bones mock API and a full-scale production application.

A true "do the simplest thing that could possibly work" approach would be a 20 line script with hard-coded JSON responses. Sufficient to get a mobile developer up and running for a few days while the API catches up? Probably. A useful coding challenge? Probably not!

The goal here was to create something more substantial than a simple mock while still keeping the focus on fundamental backend development concepts. Hopefully I struck the right balance!

## Dependencies

The API uses `quart` and `aiosqlite`. Tests use `pytest-asyncio`. These libraries are essentially just async versions of `flask`, `sqlite`, and `pytest`.

Formatting and linting use `ruff`. Type checking is handled by `pyright`.

## Application Structure

The core application logic lives in the `src/carton_caps/` directory.

### `app.py`

The entry point for the web application. It uses the application factory pattern (`create_app`), a common approach in Flask applications that allows for creating multiple instances of the app with different configurations (e.g., one for production, one for testing).

#### Database Management

The `get_db()` and `close_db()` functions manage the database connection lifecycle on a per-request basis using Quart's application context (`g`).

#### `init-db` Command

The `init-db` command provides a simple way to initialize the database schema and seed it with data.

#### API Endpoint

The single route, `/users/<int:user_id>/referrals`, handles fetching and returning referral data.

### `database.py`

This module is intended to cleanly decouple the database from the application logic. This separation of concerns can make the code easier to maintain and test.

#### `Database`

Encapsulates the raw aiosqlite connection and provides a set of async methods for all database operations.

#### `User`, `Referral`, and `ReferralUser`

Dataclasses for moving data between the database and the application.

#### `_make_user` and `_make_referral`

Factory functions used to transform raw database rows into dataclasses.

## Testing

### `conftest.py`

This file uses pytest's fixture system to provide reusable setup and teardown logic for tests.

The `app` fixture creates a new application instance with a temporary, isolated database for each test.

The `client` fixture provides a test client for making HTTP requests against the app instance.

### `test_database.py`

Tests the database in isolation. These tests use an in-memory SQLite database for speed.

### `test_app.py`

Tests that the different parts of the application work together as expected. They use the client fixture to make requests to the API endpoint and assert that the correct HTTP status codes and JSON responses are returned.

## Continuous Integration

The `.github/workflows/ci.yaml` workflow is configured to automate several code quality checks on every push. The workflow includes steps for formatting (`ruff format`), linting (`ruff check`), type checking (`pyright`), and testing (`pytest`).
