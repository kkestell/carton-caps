import pytest
import aiosqlite
import pytest_asyncio

from carton_caps.database import Database, ReferralUser


@pytest_asyncio.fixture
async def db():
    """Pytest fixture to set up and tear down an empty in-memory database."""
    database = Database(":memory:")
    await database.init_db()
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_get_user_by_id_exists(db: Database):
    """Tests that an existing user can be retrieved by id."""
    # Arrange
    mulder = await db.create_user("Fox Mulder", "TRUSTNO1")

    # Act
    user = await db.get_user_by_id(mulder.id)

    # Assert
    assert user is not None
    assert user.name == "Fox Mulder"
    assert user.referral_code == "TRUSTNO1"
    assert user.avatar_url == "https://place-hold.it/64x64"


@pytest.mark.asyncio
async def test_get_user_by_id_not_exists(db: Database):
    """Tests that a non-existent user returns None."""
    # Arrange
    id_to_find = 123

    # Act
    user = await db.get_user_by_id(id_to_find)

    # Assert
    assert user is None


@pytest.mark.asyncio
async def test_get_referrals_by_source_id_has_referrals(db: Database):
    """Tests retrieving referrals for a user who has made them."""
    # Arrange
    mulder = await db.create_user("Fox Mulder", "TRUSTNO1")
    flukeman = await db.create_user("The Flukeman", "FLUKEMAN")
    tooms = await db.create_user("Eugene Victor Tooms", "LIVERLVR")
    await db.create_referral(source_user_id=mulder.id, target_user_id=flukeman.id, status="confirmed")
    await db.create_referral(source_user_id=mulder.id, target_user_id=tooms.id, status="confirmed")

    # Act
    referrals = await db.get_referrals_by_source_id(mulder.id)

    # Assert
    assert len(referrals) == 2
    assert referrals[0].user.name == "The Flukeman"
    assert referrals[1].user.name == "Eugene Victor Tooms"


@pytest.mark.asyncio
async def test_get_referrals_by_source_id_no_referrals(db: Database):
    """Tests retrieving referrals for a user who has not made any."""
    # Arrange
    source_user = await db.create_user("The Flukeman", "FLUKEMAN")
    await db.create_user("Fox Mulder", "TRUSTNO1")

    # Act
    referrals = await db.get_referrals_by_source_id(source_user.id)

    # Assert
    assert len(referrals) == 0


@pytest.mark.asyncio
async def test_create_user_success(db: Database):
    """Tests successful creation of a new user."""
    # Arrange
    name = "Alex Krycek"
    code = "RATBOY"

    # Act
    new_user = await db.create_user(name, code)
    retrieved_user = await db.get_user_by_id(new_user.id)

    # Assert
    assert new_user.name == name
    assert new_user.referral_code == code
    assert new_user.avatar_url == "https://place-hold.it/64x64"
    assert retrieved_user is not None
    assert new_user.id == retrieved_user.id


@pytest.mark.asyncio
async def test_create_user_duplicate_name_fails(db: Database):
    """Tests that creating a user with a duplicate name raises an IntegrityError."""
    # Arrange
    name = "Fox Mulder"
    await db.create_user(name, "TRUSTNO1")

    # Act / Assert
    with pytest.raises(aiosqlite.IntegrityError):
        await db.create_user(name, "NEWCODE")


@pytest.mark.asyncio
async def test_create_referral_duplicate_target_user_fails(db: Database):
    """Tests that creating a referral with a duplicate target user raises an IntegrityError."""
    # Arrange
    source_user1 = await db.create_user("Fox Mulder", "TRUSTNO1")
    source_user2 = await db.create_user("Dana Scully", "SCULLYMD")
    target_user = await db.create_user("Walter Skinner", "SKINNERAD")
    await db.create_referral(source_user1.id, target_user.id, "confirmed")

    # Act / Assert
    with pytest.raises(aiosqlite.IntegrityError):
        await db.create_referral(source_user2.id, target_user.id, "pending")


@pytest.mark.asyncio
async def test_create_referral_success(db: Database):
    """Tests successful creation of a new referral."""
    # Arrange
    source_user = await db.create_user("Dana Scully", "SCULLYMD")
    target_user = await db.create_user("The Great Mutato", "CHERFAN")

    # Act
    new_referral = await db.create_referral(source_user.id, target_user.id, "pending")

    # Assert
    assert isinstance(new_referral.user, ReferralUser)
    assert new_referral.user.name == target_user.name
    assert new_referral.user.id == target_user.id
    assert new_referral.user.avatar_url == "https://place-hold.it/64x64"
    assert new_referral.status == "pending"

    # Verify it's in the database by fetching it
    scully_referrals = await db.get_referrals_by_source_id(source_user.id)
    assert len(scully_referrals) == 1
    assert scully_referrals[0].id == new_referral.id
    assert scully_referrals[0].user.name == target_user.name
