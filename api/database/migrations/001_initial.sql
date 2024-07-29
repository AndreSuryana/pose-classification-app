-- Create schema version table for database migrations
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    description TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create prediction history table
CREATE TABLE IF NOT EXISTS prediction_history (
    id INTEGER PRIMARY KEY,
    predictions TEXT,
    category TEXT,
    confidence REAL,
    prediction_time REAL,
    keypoints TEXT,
    timestamp TEXT
);

-- Create models table
CREATE TABLE IF NOT EXISTS models (
    id INTEGER PRIMARY KEY,
    model_path TEXT,
    timestamp TEXT
);

-- Ceate categories table that has relation to the 'models' table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY,
    model_id INTEGER,
    category_name TEXT,
    timestamp TEXT,
    FOREIGN KEY (model_id) REFERENCES models(id)
);