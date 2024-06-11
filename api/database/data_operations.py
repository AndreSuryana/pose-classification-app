import sqlite3
import time
import json

from database.connection import Database
import logger as log

db = Database()

def store_prediction_history(predictions, category, confidence, prediction_time, keypoints):
    """Store a prediction result in the database."""
    conn = db.get_connection()

    if conn is None:
        return
    
    try:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        conn.execute(
            'INSERT INTO prediction_history (predictions, category, confidence, prediction_time, keypoints, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
            (str(predictions.tolist()), category, confidence, prediction_time, str(keypoints.tolist()), timestamp)
        )
        conn.commit()
        log.i('Prediction history stored successfully')

    except sqlite3.Error as e:
        log.e(f'Error while trying to store prediction history: {e}')

    finally:
        conn.close()


def get_all_prediction_history():
    """Retrieve all prediction histories from the database."""
    conn = db.get_connection()

    try:
        # Execute query
        cursor = conn.execute('SELECT * FROM prediction_history')
        histories = cursor.fetchall()

        # Convert each row to a dictionary and parse JSON fields
        histories_dict = []

        for row in histories:
            row_dict = dict(row)
            row_dict['keypoints'] = json.loads(row_dict['keypoints'])
            row_dict['predictions'] = json.loads(row_dict['predictions'])
            histories_dict.append(row_dict)

        return histories_dict

    except sqlite3.Error as e:
        log.e(f'Error while retrieving prediction history: {e}')
        return []
    
    finally:
        conn.close()