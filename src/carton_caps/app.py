import os
from dataclasses import asdict

import click
from quart import Quart, jsonify, abort, g, current_app
from werkzeug.exceptions import HTTPException

from carton_caps.database import Database
from carton_caps.utils import make_sync


def get_db() -> Database:
    """
    Returns the database connection for the current context.

    This follows the Flask/Quart pattern of storing per-request resources
    in the 'g' object, which provides request-local storage. This allows each
    request to get its own database connection while allowing reuse within
    the same request context.
    """
    if "db" not in g:
        # Create a new database connection using the app's configured path
        g.db = Database(current_app.config["DATABASE"])
    return g.db


async def close_db(_e=None):
    """
    Closes the database connection in the current context, if it exists.

    This is registered as a teardown handler, meaning it runs automatically
    at the end of each request to clean up resources. The 'e' parameter
    receives any exception that occurred during request processing.
    """
    # Remove and get the db connection from request-local storage
    db = g.pop("db", None)
    if db is not None:
        await db.close()


@click.command("init-db")
@make_sync
async def init_db_command():
    """
    Initializes the database with seed data.

    This is a CLI command that can be run with: quart init-db
    The @make_sync decorator handles the async/sync bridge for Click.
    """
    # Create an application instance to get access to configuration
    app = create_app()

    # Use app_context() to simulate being inside a request for database access
    async with app.app_context():
        db = get_db()
        # Initialize the database
        await db.init_db()
        # Create realistic seed data for testing.
        await db.seed_db()
        click.echo("Initialized the database.")


def create_app(test_config=None, **kwargs):
    """
    Creates and afigures an instance of the application.

    This is the standard Flask/Quart application factory pattern.
    """
    # Create the Quart application instance
    app = Quart(__name__, **kwargs)

    # Set default configuration values
    # instance_path is a Flask/Quart convention for app-specific data
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "app.sqlite"),
    )

    if test_config is None:
        # In production, load configuration from a Python file
        # silent=True means prevents errors if the file doesn't exist
        app.config.from_pyfile("config.py", silent=True)
    else:
        # In testing, use the provided test configuration
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists for storing the database file
    try:
        os.makedirs(app.instance_path)
    except OSError:
        # Folder already exists, which is fine
        pass

    # Register cleanup function to run after each request
    # This is the standard pattern for resource cleanup in Flask/Quart
    app.teardown_appcontext(close_db)

    # Add a custom CLI command to the application
    app.cli.add_command(init_db_command)

    @app.errorhandler(Exception)
    async def handle_errors(e):
        """
        Global error handler for consistent JSON error responses.
        """
        # Log the error for debugging
        app.logger.error(e)

        # Handle HTTP exceptions (400, 404, etc.)
        if isinstance(e, HTTPException):
            code = e.code or 500
            return jsonify({"error": e.description}), code

        # For all other exceptions, return a generic 500 error
        # This prevents sensitive error details from leaking to clients
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/users/<int:user_id>/referrals")
    async def get_user_referrals(user_id: int):
        """
        Returns a list of referrals for a given user ID.
        """
        db = get_db()

        # First, check if the user exists in the database.
        user = await db.get_user_by_id(user_id)

        # If not, abort with a 404 error.
        if not user:
            abort(404, description=f"User with ID {user_id} not found")

        # If we were implementing authorization, we'd do that here.

        # The user exists, so get their referrals.
        referrals = await db.get_referrals_by_source_id(user_id)

        # Convert dataclass objects to dictionaries and return as JSON
        return jsonify([asdict(row) for row in referrals])

    # Return the configured application instance
    return app
