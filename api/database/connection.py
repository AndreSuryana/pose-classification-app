import sqlite3
import os

import logger as log

class Database:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_name = os.getenv('API_DB', 'database.db')
        self.db_path = os.path.join(base_dir, db_name)
        self.migrations_dir = os.path.join(base_dir, 'migrations')

    def apply_migrations(self):
        """Apply database migrations."""
        log.i('Starting database migration process.')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check current version
        current_version = 0
        log.i('Checking current schema version.')
        try:
            cursor.execute("SELECT version FROM schema_version ORDER BY applied_at DESC LIMIT 1")
            row = cursor.fetchone()
            current_version = row[0] if row else 0
            log.i(f'Current schema version: {current_version}')
        except sqlite3.Error as e:
            log.e(f'Error connecting to database: {e}')

        # Apply migrations
        for filename in sorted(os.listdir(self.migrations_dir)):
            if filename.endswith('.sql'):
                version = int(filename.split('_')[0])
                if version > current_version:
                    log.i(f'Applying migration: {filename}')
                    with open(os.path.join(self.migrations_dir, filename), 'r') as f:
                        script = f.read()
                        cursor.executescript(script)
                        cursor.execute("INSERT INTO schema_version (version, description) VALUES (?, ?)", (version, filename))
                        conn.commit()
                        log.i(f'Migration {filename} applied successfully.')

        conn.close()
        log.i('Database migration process completed.')

    def get_connection(self):
        """Get a connection to the SQLite database."""
        if not os.path.exists(self.db_path):
            log.i('Database not found. Applying migrations.')
        else:
            log.i('Database found. Checking for required migrations.')

        self.apply_migrations()

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            log.i('Database connection established.')
            return conn

        except sqlite3.Error as e:
            log.e(f'Error connecting to database: {e}')
            return None
