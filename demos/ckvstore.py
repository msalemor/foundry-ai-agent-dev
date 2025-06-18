import threading
import sqlite3
import json
from typing import Dict, Any, Optional, List

from logger import get_logger

logger = get_logger(__name__)


class CategoryKeyValueStore:
    def __init__(self, db_path: str = "./store.db"):
        self.db_path = db_path
        self._lock = threading.RLock()
        self._init_db()

    def _init_db(self):
        """Initialize the database and create table if it doesn't exist."""
        with self._lock:
            logger.info(f"Initializing database at {self.db_path}")
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS store (
                        category TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL,
                        PRIMARY KEY (category, key)
                    )
                """
                )
                conn.commit()

    def set(self, category: str, key: str, value: Any) -> None:
        """Set a value for a given category and key."""
        logger.info(f"Setting value for category '{category}', key '{key}'")
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO store (category, key, value)
                    VALUES (?, ?, ?)
                """,
                    (category, key, json.dumps(value)),
                )
                conn.commit()

    def get(self, category: str, key: str) -> Optional[Any]:
        """Get a value for a given category and key."""
        logger.info(f"Getting value for category '{category}', key '{key}'")
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT value FROM store
                    WHERE category = ? AND key = ?
                """,
                    (category, key),
                )
                row = cursor.fetchone()
                return json.loads(row[0]) if row else None

    def delete(self, category: str, key: str) -> bool:
        """Delete a key from a category. Returns True if deleted, False if not found."""
        logger.info(f"Deleting key '{key}' from category '{category}'")
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    DELETE FROM store
                    WHERE category = ? AND key = ?
                """,
                    (category, key),
                )
                conn.commit()
                return cursor.rowcount > 0

    def delete_category(self, category: str) -> bool:
        """Delete an entire category. Returns True if deleted, False if not found."""
        logger.info(f"Deleting category '{category}'")
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    DELETE FROM store
                    WHERE category = ?
                """,
                    (category,),
                )
                conn.commit()
                return cursor.rowcount > 0

    def get_category(self, category: str) -> Dict[str, Any]:
        """Get all key-value pairs in a category."""
        logger.info(f"Getting all items in category '{category}'")
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT key, value FROM store
                    WHERE category = ?
                """,
                    (category,),
                )
                return {row[0]: json.loads(row[1]) for row in cursor.fetchall()}

    def get_categories(self) -> List[str]:
        """Get all category names."""
        logger.info("Getting all categories")
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    SELECT DISTINCT category FROM store
                    ORDER BY category
                """
                )
                return [row[0] for row in cursor.fetchall()]

    def exists(self, category: str, key: Optional[str] = None) -> bool:
        """Check if a category or category/key combination exists."""
        logger.info(
            f"Checking existence for category '{category}'"
            + (f", key '{key}'" if key else "")
        )
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                if key is None:
                    cursor = conn.execute(
                        """
                        SELECT 1 FROM store
                        WHERE category = ?
                        LIMIT 1
                    """,
                        (category,),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT 1 FROM store
                        WHERE category = ? AND key = ?
                        LIMIT 1
                    """,
                        (category, key),
                    )
                return cursor.fetchone() is not None

    def clear(self) -> None:
        """Clear all data from the store."""
        logger.info("Clearing all data from the store")
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM store")
                conn.commit()

    def size(self, category: Optional[str] = None) -> int:
        """Get the number of keys in a category or total number of categories."""
        logger.info(
            f"Getting size for category '{category}'"
            if category
            else "Getting total number of categories"
        )
        with self._lock:
            with sqlite3.connect(self.db_path) as conn:
                if category is None:
                    cursor = conn.execute(
                        """
                        SELECT COUNT(DISTINCT category) FROM store
                    """
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT COUNT(*) FROM store
                        WHERE category = ?
                    """,
                        (category,),
                    )
                return cursor.fetchone()[0]


# Example usage
if __name__ == "__main__":
    store = CategoryKeyValueStore()

    # Set values
    store.set("users", "user1", {"name": "Alice", "age": 30})
    store.set("users", "user2", {"name": "Bob", "age": 25})
    store.set("settings", "theme", "dark")
    store.set("settings", "language", "en")

    # Get values
    print(store.get("users", "user1"))  # {'name': 'Alice', 'age': 30}
    print(store.get("settings", "theme"))  # dark

    # Get entire category
    print(store.get_category("settings"))  # {'theme': 'dark', 'language': 'en'}

    # Check existence
    print(store.exists("users", "user1"))  # True
    print(store.exists("users"))  # True

    # Delete operations
    store.delete("settings", "theme")
    store.delete_category("users")

    # Get all categories
    print(store.get_categories())  # ['settings']
