from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError
from werkzeug.utils import secure_filename
from pydantic import BaseModel, ValidationError, conlist
from typing import List

import tensorflow as tf
import numpy as np
from sklearn.preprocessing import LabelEncoder

import pandas as pd
from io import BytesIO

import os
import time
import threading

from helper import preprocess_keypoints, check_allowed_files
from database.data_operations import store_prediction_history, get_all_prediction_history
from database.connection import Database

import logger as log


# Create Flask app
app = Flask(__name__)

# Define the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# File Uploads Configurations
UPLOAD_FOLDER = os.path.join(base_dir, 'uploads')
MODEL_ALLOWED_EXTENSIONS = {'keras'}
CATEGORY_ALLOWED_EXTENSIONS = {'txt'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Global variables to store the model and categories
model = None
label_encoder = LabelEncoder()
categories = []

def load_latest_model_and_categories():
    global model, categories, label_encoder

    conn = Database().get_connection()
    cursor = conn.cursor()

    try:
        # Fetch the latest model and its categories from the database
        cursor.execute("""
            SELECT models.model_path, categories.category_name
            FROM models
            JOIN categories ON models.id = categories.model_id
            ORDER BY models.timestamp DESC, categories.timestamp DESC
        """)
        rows = cursor.fetchall()

        if rows:
            model_path = rows[0][0]
            categories = [row[1].strip() for row in rows]

            # Load the latest model
            model = tf.keras.models.load_model(model_path)

            # Fit the LabelEncoder with the latest categories
            label_encoder.fit(categories)

            log.i("Latest model and categories loaded successfully")
        else:
            log.w("No model found in the database. The application will start without a model.")
    
    except Exception as e:
        log.e(f"Failed to load latest model and categories: {str(e)}")
    
    finally:
        conn.close()

def load_model_and_categories(model_path, category_lines):
    global model, categories, label_encoder

    try:
        # Load the TensorFlow model
        model = tf.keras.models.load_model(model_path)

        # Update the categories
        categories = [line.strip() for line in category_lines]
        label_encoder.fit(categories)

        log.i("Model and categories loaded successfully")

    except Exception as e:
        log.e(f"Failed to load model and categories: {str(e)}")

# Define request schema for prediction request
class PredictRequest(BaseModel):
    keypoints: List[conlist(item_type=float, min_length=3, max_length=3)] # type: ignore

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check for model initialization
        if model is None:
            raise InternalServerError("Model is not initialized. Please update the model.")

        # Parse and validate the request data
        data = PredictRequest(**request.get_json())
        
        # Convert into numpy array
        keypoints = np.array(data.keypoints)

        # Prepare feature for prediction
        features = preprocess_keypoints(keypoints)

        # Start time before the prediction
        start_time = time.time()

        # Make prediction
        log.i('Starting the prediction...')
        log.d('Features: ', features)
        predictions = model.predict(features)

        # End time after the prediction
        end_time = time.time()

        # Calculate the elapsed prediction time
        prediction_time = round(end_time - start_time, 6)

        # Get the index of the highest probability
        predicted_idx = np.argmax(predictions, axis=1)
        predicted_category = label_encoder.inverse_transform(predicted_idx)[0]

        # Get the confidence rate
        confidence = float(np.max(predictions, axis=1)[0])

        # Log the results
        log.d('Predictions: ', predictions)
        log.d('Predicted category idx: ', predicted_idx)
        log.i('Predicted category: ', predicted_category)
        log.i('Confidence: ', confidence)
        log.i('Prediction time: {} seconds'.format(prediction_time))

        # Store the prediction result and keypoints in the database
        store_prediction_history(predictions, predicted_category, confidence, prediction_time, keypoints)

        return jsonify({
            'prediction': predicted_category,
            'confidence': confidence,
            'prediction_time': prediction_time
        })
    
    except ValidationError as e:
        # ValidationError return a list of error, just use the first error found
        return handle_custom_exception(e.errors()[0]['msg'], 403)

@app.route('/model-update', methods=['POST'])
def model_update():
    # Ensure 'model' and 'category' keys are in the request
    if 'model' not in request.files or 'category' not in request.files:
        raise BadRequest("Missing 'model' or 'category' file part")
    
    # Retrieve the request files
    model_file = request.files['model']
    category_file = request.files['category']

    # Ensure there are selected files in the request
    if model_file.filename == '':
        raise BadRequest("No selected file for 'model'")
    elif category_file.filename == '':
        raise BadRequest("No selected file for 'category'")
    
    # Validate the 'model' file extension
    if not check_allowed_files(model_file.filename, MODEL_ALLOWED_EXTENSIONS):
        raise BadRequest(f"Invalid file type for 'model': {model_file.filename}. Expected .keras")

    # Validate the 'category' file extension
    if not check_allowed_files(category_file.filename, CATEGORY_ALLOWED_EXTENSIONS):
        raise BadRequest(f"Invalid file type for 'category': {category_file.filename}. Expected .txt")

    # Check that the 'category' file is not empty and store each line into an array
    category_file_content = category_file.read().decode('utf-8').strip()
    if not category_file_content:
        raise BadRequest("'category' file is empty")

    category_lines = category_file_content.split('\n')
    if not category_lines:
        raise BadRequest("'category' file contains no lines")
    
    # Reset the file pointer to the beginning after reading
    category_file.seek(0)
    
    # Process the 'model' file
    model_filename = secure_filename(model_file.filename)
    model_path = os.path.join(app.config['UPLOAD_FOLDER'], model_filename)

    conn = None
    try:
        # Save the model file into the upload folder
        model_file.save(model_path)

        # Connect to the database
        conn = Database().get_connection()
        cursor = conn.cursor()

        # Insert the model path into the 'models' table
        cursor.execute("INSERT INTO models (model_path, timestamp) VALUES (?, datetime('now'))", (model_path,))
        model_id = cursor.lastrowid

        # Insert the categories into the 'categories' table
        for category in category_lines:
            cursor.execute("INSERT INTO categories (model_id, category_name, timestamp) VALUES (?, ?, datetime('now'))", (model_id, category))
        
        # Commit the transaction
        conn.commit()

        # Start the background thread to load the latest model and categories
        threading.Thread(target=load_model_and_categories, args=(model_path, category_lines)).start()

        return jsonify({"message": "Model and categories update initiated"}), 201
    
    except Exception as e:
        if conn:
            conn.rollback() # Rollback any changes if an errors occurs
        raise InternalServerError(f"Failed to update model and categories: {str(e)}")

    finally:
        if conn:
            conn.close()

@app.route('/history', methods=['GET'])
def get_prediction_history():
    # Retrieve the histories
    histories = get_all_prediction_history()
    
    # Log the results
    log.d('Histories: ', histories)

    # Get the format parameter
    format = request.args.get('format', 'json').lower()
    log.d('Expected format: ', format)

    # Compose response according to the requested format
    if format == 'xlsx':
        # Convert into DataFrame
        # TODO: Match the exported xlsx with the dataset from the CNN Model Training Datasets
        df = pd.DataFrame(histories, columns=['id', 'predictions', 'category', 'confidence', 'prediction_time', 'keypoints', 'timestamp'])
    
        # Create an in-memory output file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Histories')

        # Set the buffer position to the beginning of the stream
        output.seek(0)

        # Create a response with the Excel file
        response = make_response(output.read())
        response.headers['Content-Disposition'] = 'attachment; filename=prediction_history.xlsx'
        response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        return response
    
    elif format == 'json':
        return jsonify({
            'count': len(histories),
            'histories': histories
        })
    
    else:
        raise BadRequest(f"Unsupported format: {format}. Supported formats are 'json' and 'xlsx'.")

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    response = e.get_response()
    return handle_custom_exception(e.description, e.code)

def handle_custom_exception(error, code):
    """Return JSON for custom errors."""
    return jsonify({'message': error}), code
    

if __name__ == '__main__':
    # Debugging flag
    debuggable = os.getenv('APP_ENV') == 'development'

    # Configure server before run
    host = os.getenv('API_HOST', 'localhost')
    port = os.getenv('API_PORT', '5000')

    # Ensure the latest model and categories are loaded at startup
    load_latest_model_and_categories()
    
    app.run(host, port, debuggable)