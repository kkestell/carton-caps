import os
import tempfile

import pytest
import pytest_asyncio

from carton_caps.app import create_app, get_db


@pytest_asyncio.fixture
async def app():
    """Creates and configures a new app instance for each test."""
    with tempfile.TemporaryDirectory() as instance_path:
        db_path = os.path.join(instance_path, "test.sqlite")

        app = create_app(
            test_config={
                "TESTING": True,
                "DATABASE": db_path,
            },
            instance_path=instance_path,
        )

        async with app.app_context():
            # Get the database instance for the current context and initialize it.
            db = get_db()
            await db.init_db()

        yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()
