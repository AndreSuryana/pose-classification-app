import sqlite3
import os

import logger as log

class Database:
    def __init__(self):
        self.db_name = os.getenv('DB_NAME', 'database.db')

    def init_database(self):
        """Initialize the database by creating the required tables."""
        try:
            # Init database connection
            conn = sqlite3.connect(self.db_name)
            
            # Run schema.sql
            with open('database/schema.sql') as s:
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
        if not os.path.exists(self.db_name):
            self.init_database()

        try:
            # Trying to establish database connection
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            log.i('Database connection established.')

            return conn
        
        except sqlite3.Error as e:
            log.e(f'Error connecting to database: {e}')
            return None