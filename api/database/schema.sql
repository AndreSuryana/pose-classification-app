-- Create prediction history table
CREATE TABLE IF NOT EXISTS prediction_history (
    id INTEGER PRIMARY KEY,
    predictions TEXT,
    category TEXT,
    confidence REAL,
    prediction_time REAL,
    keypoints TEXT,
    timestamp TEXT
)