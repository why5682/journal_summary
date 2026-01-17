"""
Paper Storage Module
SQLite-based storage for tracking processed papers.
"""
import sqlite3
import logging
from typing import Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PaperStorage:
    """Manages SQLite database for tracking processed papers."""

    def __init__(self, db_path: str = "paper_history.db"):
        """
        Initialize storage with database path.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the database table if it does not exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS processed_papers (
                        id TEXT PRIMARY KEY,
                        title TEXT,
                        journal TEXT,
                        summary TEXT,
                        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
                logger.info(f"Database initialized: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def is_processed(self, paper_id: str) -> bool:
        """Check if a paper has already been processed."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT 1 FROM processed_papers WHERE id = ?", 
                    (paper_id,)
                )
                return cursor.fetchone() is not None
        except sqlite3.Error as e:
            logger.error(f"Database error during check: {e}")
            return False

    def add_paper(
        self, 
        paper_id: str, 
        title: str, 
        journal: str = "",
        summary: str = ""
    ) -> None:
        """Record a paper as processed."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT OR REPLACE INTO processed_papers 
                       (id, title, journal, summary) VALUES (?, ?, ?, ?)""",
                    (paper_id, title, journal, summary)
                )
                conn.commit()
                logger.debug(f"Added paper: {title[:50]}...")
        except sqlite3.Error as e:
            logger.error(f"Failed to add paper to database: {e}")

    def get_processed_count(self) -> int:
        """Get the total number of processed papers."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM processed_papers")
                return cursor.fetchone()[0]
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return 0

    def clear_history(self) -> None:
        """Clear all processed paper history."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM processed_papers")
                conn.commit()
                logger.info("Cleared paper history")
        except sqlite3.Error as e:
            logger.error(f"Failed to clear history: {e}")
