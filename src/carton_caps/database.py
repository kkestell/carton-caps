from dataclasses import dataclass
from datetime import datetime, UTC

import aiosqlite


@dataclass
class User:
    """Represents a user in the system."""

    id: int
    name: str
    avatar_url: str
    referral_code: str


@dataclass
class ReferralUser:
    """Represents a simplified user for the context of a referral."""

    id: int
    name: str
    avatar_url: str


@dataclass
class Referral:
    """Represents a referral relationship between two users."""

    id: int
    user: ReferralUser
    status: str
    created_at: str


def _make_user(row: aiosqlite.Row) -> User:
    """Creates a User from a database row."""
    return User(
        id=row["id"],
        name=row["name"],
        avatar_url="https://place-hold.it/64x64",
        referral_code=row["referral_code"],
    )


def _make_referral(row: aiosqlite.Row) -> Referral:
    """Creates a Referral from a database row."""
    return Referral(
        id=row["id"],
        user=ReferralUser(
            id=row["user_id"],
            name=row["name"],
            avatar_url="https://place-hold.it/64x64",
        ),
        status=row["status"],
        created_at=row["created_at"],
    )


class Database:
    def __init__(self, path: str):
        self._path = path
        self._conn = None

    async def get_conn(self) -> aiosqlite.Connection:
        """Returns the database connection, creating it if it doesn't exist."""
        if not self._conn:
            self._conn = await aiosqlite.connect(self._path)
            self._conn.row_factory = aiosqlite.Row
        return self._conn

    async def close(self) -> None:
        """Closes the database connection."""
        if self._conn is not None:
            await self._conn.close()
            self._conn = None

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieves a single user by their id."""
        conn = await self.get_conn()
        async with conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return _make_user(row) if row else None

    async def get_referrals_by_source_id(self, source_id: int) -> list[Referral]:
        """Retrieves all referrals initiated by a specific user."""
        conn = await self.get_conn()
        async with conn.execute(
            """
            SELECT
                r.id,
                u.id as user_id,
                u.name,
                r.status,
                r.created_at
            FROM referrals r
            JOIN users u ON r.target_user_id = u.id
            WHERE r.source_user_id = ?
            """,
            (source_id,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [_make_referral(row) for row in rows]

    async def create_user(self, name: str, referral_code: str) -> User:
        """Creates a new user in the database and returns it."""
        conn = await self.get_conn()
        async with conn.execute(
            "INSERT INTO users (name, referral_code) VALUES (?, ?)",
            (name, referral_code),
        ) as cursor:
            user_id = cursor.lastrowid
        await conn.commit()

        async with conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            new_user = await cursor.fetchone()

        if new_user is None:
            raise RuntimeError("Failed to create or retrieve user after insertion.")

        return _make_user(new_user)

    async def create_referral(self, source_user_id: int, target_user_id: int, status: str) -> Referral:
        """Creates a new referral in the database and returns it."""
        conn = await self.get_conn()
        now = datetime.now(UTC).isoformat()
        async with conn.execute(
            "INSERT INTO referrals (source_user_id, target_user_id, created_at, status) VALUES (?, ?, ?, ?)",
            (source_user_id, target_user_id, now, status),
        ) as cursor:
            referral_id = cursor.lastrowid
        await conn.commit()

        async with conn.execute(
            """
            SELECT
                r.id,
                u.id as user_id,
                u.name,
                r.status,
                r.created_at
            FROM referrals r
            JOIN users u ON r.target_user_id = u.id
            WHERE r.id = ?
            """,
            (referral_id,),
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            raise RuntimeError("Failed to create or retrieve referral after insertion.")

        return _make_referral(row)

    async def init_db(self) -> None:
        """Initializes the database schema."""
        conn = await self.get_conn()

        await conn.executescript(
            """
            DROP TABLE IF EXISTS referrals;
            DROP TABLE IF EXISTS users;

            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT(256) NOT NULL UNIQUE,
                referral_code TEXT(16) NOT NULL UNIQUE
            );

            CREATE TABLE referrals (
                id INTEGER PRIMARY KEY,
                source_user_id INTEGER NOT NULL,
                target_user_id INTEGER NOT NULL UNIQUE,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (source_user_id) REFERENCES users(id) ON DELETE RESTRICT,
                FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE RESTRICT
            );
            """
        )
        await conn.commit()

    async def seed_db(self) -> None:
        """Creates realistic seed data for testing."""
        mulder = await self.create_user("Fox Mulder", "TRUSTNO1")
        scully = await self.create_user("Dana Scully", "SCULLYMD")
        skinner = await self.create_user("Walter Skinner", "SKINNERAD")
        spender = await self.create_user("C.G.B. Spender", "CANCERMAN")
        flukeman = await self.create_user("The Flukeman", "FLUKEMAN")
        tooms = await self.create_user("Eugene Victor Tooms", "LIVERLVR")
        mutato = await self.create_user("The Great Mutato", "CHERFAN")
        betts = await self.create_user("Leonard Betts", "REGENERATE")

        await self.create_referral(source_user_id=spender.id, target_user_id=skinner.id, status="confirmed")
        await self.create_referral(source_user_id=skinner.id, target_user_id=mulder.id, status="confirmed")
        await self.create_referral(source_user_id=skinner.id, target_user_id=scully.id, status="confirmed")
        await self.create_referral(source_user_id=mulder.id, target_user_id=flukeman.id, status="confirmed")
        await self.create_referral(source_user_id=mulder.id, target_user_id=tooms.id, status="confirmed")
        await self.create_referral(source_user_id=mulder.id, target_user_id=mutato.id, status="pending")
        await self.create_referral(source_user_id=mulder.id, target_user_id=betts.id, status="pending")
