from flask import Flask, request, jsonify, make_response
from werkzeug.exceptions import HTTPException, BadRequest
from pydantic import BaseModel, ValidationError, conlist
from typing import List
from dotenv import load_dotenv

import tensorflow as tf
import numpy as np
from sklearn.preprocessing import LabelEncoder

import pandas as pd
from io import BytesIO

import os
import time

from helper import preprocess_keypoints, load_categories
from database.data_operations import store_prediction_history, get_all_prediction_history

import logger as log


# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Load the TensorFlow model
model = tf.keras.models.load_model('cnn/model.keras')

# Define the class labels or categories in this case
categories = load_categories('cnn/categories.txt')

# Fit the LabelEncoder with the class labels
label_encoder = LabelEncoder()
label_encoder.fit(categories)

# Define request schema for prediction request
class PredictRequest(BaseModel):
    keypoints: List[conlist(item_type=float, min_length=3, max_length=3)] # type: ignore

@app.route('/predict', methods=['POST'])
def predict():
    try:
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
    debuggable = os.getenv('FLASK_ENV') != 'production'

    # Configure server before run
    host = os.getenv('SERVER_HOSTNAME', None)
    port = os.getenv('SERVER_PORT', None)
    
    app.run(host, port, port)