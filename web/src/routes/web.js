const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');
const axios = require('axios');
const logger = require('../middleware/logger');
const config = require('../config');
const { detectKeypoints, addOverlayToImage, resizeImage } = require('../movenet/movenet');
const { loadImage } = require('canvas');

const router = express.Router();

// Multer storage configuration
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Create the uploads directory if it doesn't exist
const uploadsDir = 'public/uploads';
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
}

// Main page to upload the image
router.get('/', (req, res) => {
    try {
        res.render('index');
    } catch (error) {
        logger.error(`Error rendering main page: ${error.message}`);
        res.status(500).send('Server error');
    }
});

// Handle if user accidentally access the predict enpoint using GET method 
router.get('/predict', (req, res) => {
    res.redirect('/');
});

// Predict the keypoints
router.post('/predict', upload.single('image'), async (req, res) => {
    try {
        // Record start time
        const startTime = Date.now();

        // Retrieve the image file buffer
        const imageBuffer = req.file.buffer;

        // Load the image from buffer
        const image = await loadImage(imageBuffer);

        // Resize the image if it's too large
        const maxWidth = 1024; // Define maximum width
        const maxHeight = 1024; // Define maximum height
        const resizedCanvas = await resizeImage(image, maxWidth, maxHeight);
        const resizedImageBuffer = resizedCanvas.toBuffer('image/jpeg');

        // Save the resized image locally
        const imageFileName = `image_${Date.now()}.jpg`;
        const imagePath = path.join(uploadsDir, imageFileName);
        fs.writeFileSync(imagePath, resizedImageBuffer);

        // Process image using MoveNet model to retrieve keypoints
        const keypoints = await detectKeypoints(imagePath);
        const keypointsProcessedTime = Date.now();

        // Add overlay to the image based on keypoints
        var processedImagePath = await addOverlayToImage(imagePath, keypoints);
        const overlayAddedTime = Date.now();

        // Remove the 'public' directory because it's already configured as a static folder
        processedImagePath = processedImagePath.replace('public/', '');

        // Predict keypoints using the API
        const response = await axios.post(`${config.API_BASE_URL}/predict`, { keypoints });
        const apiPredictionTime = Date.now();

        // Calculate consumed time in seconds
        const consumedTime = (apiPredictionTime - startTime) / 1000;

        // Logging
        logger.info(`Response: ${JSON.stringify(response.data)}`);
        logger.debug(`Time taken to process keypoints: ${keypointsProcessedTime - startTime}ms`);
        logger.debug(`Time taken to add overlay: ${overlayAddedTime - keypointsProcessedTime}ms`);
        logger.debug(`Time taken for API prediction: ${apiPredictionTime - overlayAddedTime}ms`);
        logger.debug(`Total time consumed: ${consumedTime}`);

        // Clearing files
        fs.unlink(imagePath, (err) => {
            if (err) {
                logger.error(`Error deleting file ${imagePath}: ${err.message}`);
            } else {
                logger.debug(`Deleted file: ${imagePath}`);
            }
        });

        res.render('result', {
            processedImage: processedImagePath,
            confidence: response.data.confidence,
            predictedCategory: mapPredictionCategory(response.data.prediction),
            predictionTime: response.data.prediction_time,
            consumedTime: consumedTime,
        });
    } catch (error) {
        if (error.response) {
            // The request was made, and the server responded with a status code
            // that falls out of the range of 2xx
            logger.error(`API error response: ${JSON.stringify(error.response.data)}`);
            return res.status(error.response.status).send(`API Error: ${error.response.data.message}`);
        }

        logger.error(`Error fetching data: ${error.message}`);
        res.status(500).send('Server error');
    }
});

const mapPredictionCategory = (category) => {
    switch (category) {
        case 'good': return 'Baik';
        case 'bad': return 'Buruk';
        default: return category;
    }
}

module.exports = router 