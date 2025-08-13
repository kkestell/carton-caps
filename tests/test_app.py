import pytest

from carton_caps.app import get_db


@pytest.mark.asyncio
async def test_get_user_referrals_success(app, client):
    """Tests retrieving referrals for a user with existing referrals."""
    # Arrange
    async with app.app_context():
        db = get_db()

        # Create the user who is the source of the referrals
        mulder = await db.create_user("Fox Mulder", "TRUSTNO1")

        # Create the users who were referred
        flukeman = await db.create_user("The Flukeman", "FLUKEMAN")
        tooms = await db.create_user("Eugene Victor Tooms", "LIVERLVR")
        mutato = await db.create_user("The Great Mutato", "CHERFAN")
        betts = await db.create_user("Leonard Betts", "REGENERATE")

        # Create the referral relationships
        await db.create_referral(mulder.id, flukeman.id, "confirmed")
        await db.create_referral(mulder.id, tooms.id, "confirmed")
        await db.create_referral(mulder.id, mutato.id, "pending")
        await db.create_referral(mulder.id, betts.id, "pending")

    # Act
    response = await client.get(f"/users/{mulder.id}/referrals")

    # Assert
    assert response.status_code == 200
    data = await response.get_json()
    assert len(data) == 4
    response_names = {item["user"]["name"] for item in data}
    expected_names = {
        "The Flukeman",
        "Eugene Victor Tooms",
        "The Great Mutato",
        "Leonard Betts",
    }
    assert response_names == expected_names


@pytest.mark.asyncio
async def test_get_user_referrals_no_referrals(client, app):
    """Tests retrieving referrals for a user who hasn't made any."""
    # Arrange
    async with app.app_context():
        db = get_db()
        scully = await db.create_user("Dana Scully", "SCULLYMD")

    # Act
    response = await client.get(f"/users/{scully.id}/referrals")

    # Assert
    assert response.status_code == 200
    data = await response.get_json()
    assert len(data) == 0


@pytest.mark.asyncio
async def test_get_user_referrals_not_found(client):
    """Tests that a 404 is returned for a non-existent user."""
    # Arrange
    user_id = 999

    # Act
    response = await client.get(f"/users/{user_id}/referrals")

    # Assert
    assert response.status_code == 404
    data = await response.get_json()
    assert data["error"] == f"User with ID {user_id} not found"
