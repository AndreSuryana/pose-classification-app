import sqlite3
import os

import logger as log

class Database:
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_name = os.getenv('DB_NAME', 'database.db')
        self.db_path = os.path.join(base_dir, db_name)
        self.db_schema = os.path.join(base_dir, 'schema.sql')

    def init_database(self):
        """Initialize the database by creating the required tables."""
        try:
            # Init database connection
            conn = sqlite3.connect(self.db_path)
            
            # Run schema.sql
            with open(self.db_schema) as s:
                log.d(f'Schema: ', s)
                conn.executescript(s.read())
            
            # Commit changes and close connection
            conn.commit()
            log.i('Database initialized successfully.')

        except sqlite3.Error as e:
            log.e(f'Error initializing database: {e}')

        finally:
            conn.close()

    def get_connection(self):
        """Get a connection to the SQLite database."""
        if not os.path.exists(self.db_path):
            self.init_database()

        try:
            # Trying to establish database connection
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            log.i('Database connection established.')

            return conn
        
        except sqlite3.Error as e:
            log.e(f'Error connecting to database: {e}')
            return None