import sqlite3


class DatabaseHandler:
    def __init__(self, db_name="music_db.sqlite"):
        self.db_name = db_name
        self.connection = None
        self.create_tables()

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        return self.connection.cursor()

    def commit(self):
        if self.connection:
            self.connection.commit()

    def rollback(self):
        if self.connection:
            self.connection.rollback()

    def close(self):
        if self.connection:
            self.connection.close()

    def create_tables(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS fingerprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_id TEXT,
            time_offset INTEGER,
            timestamp TEXT,
            hashed_fingerprint TEXT
        )
        """
        )

        conn.commit()
        conn.close()

    def clear_songs(self):
        try:
            cursor = self.connect()
            cursor.execute("DELETE FROM fingerprints")
            self.commit()
            return True, "All songs cleared"
        except sqlite3.Error as e:
            self.rollback()
            return False, str(e)
        finally:
            self.close()
