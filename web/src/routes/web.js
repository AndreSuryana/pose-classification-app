const express = require('express');
const multer = require('multer');
const fs = require('fs');
const axios = require('axios');
const logger = require('../middleware/logger');
const config = require('../config');
const { detectKeypoints, addOverlayToImage } = require('../movenet/movenet');

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

        // Retrieve the image file and save it locally
        const imageBuffer = req.file.buffer;
        const imageFileName = `image_${Date.now()}.jpg`;
        const imagePath = `${uploadsDir}/${imageFileName}`;
        fs.writeFileSync(imagePath, imageBuffer);

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
        logger.info(`Time taken to process keypoints: ${keypointsProcessedTime - startTime}ms`);
        logger.info(`Time taken to add overlay: ${overlayAddedTime - keypointsProcessedTime}ms`);
        logger.info(`Time taken for API prediction: ${apiPredictionTime - overlayAddedTime}ms`);
        logger.info(`Total time consumed: ${consumedTime}`);

        res.render('result', {
            processedImage: processedImagePath,
            confidence: response.data.confidence,
            predictedCategory: response.data.prediction,
            predictionTime: response.data.prediction_time,
            consumedTime: consumedTime,
        });
    } catch (error) {
        logger.error(`Error fetching data: ${error.message}`);
        res.status(500).send('Server error');
    }
});

module.exports = router 