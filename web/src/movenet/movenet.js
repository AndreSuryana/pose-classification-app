const tf = require('@tensorflow/tfjs');
require('@tensorflow/tfjs-node');
const poseDetection = require('@tensorflow-models/pose-detection');
const { createCanvas, loadImage } = require('canvas');
const fs = require('fs');
const logger = require('../middleware/logger');

// Keypoint edges to colors
const KEYPOINT_EDGE_INDS_TO_COLOR = [
    { start: 0, end: 1, color: 'magenta' },
    { start: 0, end: 2, color: 'cyan' },
    { start: 1, end: 3, color: 'magenta' },
    { start: 2, end: 4, color: 'cyan' },
    { start: 0, end: 5, color: 'magenta' },
    { start: 0, end: 6, color: 'cyan' },
    { start: 5, end: 7, color: 'magenta' },
    { start: 7, end: 9, color: 'magenta' },
    { start: 6, end: 8, color: 'cyan' },
    { start: 8, end: 10, color: 'cyan' },
    { start: 5, end: 6, color: 'yellow' },
    { start: 5, end: 11, color: 'magenta' },
    { start: 6, end: 12, color: 'cyan' },
    { start: 11, end: 12, color: 'yellow' },
    { start: 11, end: 13, color: 'magenta' },
    { start: 13, end: 15, color: 'magenta' },
    { start: 12, end: 14, color: 'cyan' },
    { start: 14, end: 16, color: 'cyan' }
];

/**
 * Asynchronously loads the MoveNet model if it's not already loaded.
 * If the model is already loaded, this function does nothing.
 * @returns {Promise<void>} - A promise that resolves when the model is loaded or if it's already loaded.
 * @throws Will throw an error if model loading fails.
 */
const initializeMoveNetModel = async () => {
    try {
        logger.info('Loading MoveNet model...');
        const detector = await poseDetection.createDetector(
            poseDetection.SupportedModels.MoveNet, {
            modelType: poseDetection.movenet.modelType.SINGLEPOSE_THUNDER,
        });
        logger.info('MoveNet model loaded successfully');
        return detector;
    } catch (error) {
        logger.error(`Error loading MoveNet model: ${error.message}`);
        throw new Error(`Error loading MoveNet model: ${error.message}`);
    }
}

/**
 * Detect keypoints in the given image using MoveNet model.
 * @param {string} imagePath - The path to the image file.
 * @returns {Promise<Array>} - A promise that resolves to an array of keypoints.
 * @throws Will throw an error if keypoint detection fails.
 */
const detectKeypoints = async (imagePath) => {
    try {
        logger.info(`Starting keypoints detection for image: ${imagePath}`);

        // Load the image
        const image = await loadImage(imagePath);
        const canvas = createCanvas(image.width, image.height);
        const ctx = canvas.getContext('2d');
        ctx.drawImage(image, 0, 0, image.width, image.height);

        // Retrieve the detector from the global
        const detector = global.detector;

        // Estimate poses to retrieve the keypoints
        const poses = await detector.estimatePoses(canvas);
        const keypoints = extractKeypoints(poses, image.width, image.height);
        logger.info(`Keypoints detected: ${JSON.stringify(keypoints)}`);

        return keypoints;
    } catch (error) {
        logger.error(`Error processing image: ${error.message}`);
        throw new Error(`Error processing image: ${error.message}`);
    }
}

/**
 * Extract and normalize keypoints from detected poses.
 * @param {Array} poses - The detected poses from the MoveNet model.
 * @param {number} imageWidth - The width of the image.
 * @param {number} imageHeight - The height of the image.
 * @returns {Array} - An array of normalized keypoints.
 * @throws Will throw an error if no keypoints are detected.
 */
const extractKeypoints = (poses, imageWidth, imageHeight) => {
    if (poses.length > 0) {
        const keypoints = poses[0].keypoints.map(keypoint => [
            keypoint.x / imageWidth,
            keypoint.y / imageHeight,
            keypoint.score
        ]);
        return keypoints;
    } else {
        logger.warn('No keypoints detected');
        throw new Error('No keypoints detected');
    }
}

/**
 * Add overlay of keypoints to the image and save the processed image.
 * @param {string} imagePath - The path to the original image file.
 * @param {Array} keypoints - The keypoints to overlay on the image.
 * @returns {Promise<string>} - A promise that resolves to the path of the processed image.
 * @throws Will throw an error if adding overlay to image fails.
 */
const addOverlayToImage = async (imagePath, keypoints) => {
    try {
        // Load the image
        const image = await loadImage(imagePath);
        const canvas = createCanvas(image.width, image.height);
        const ctx = canvas.getContext('2d');
        ctx.drawImage(image, 0, 0, image.width, image.height);

        // Draw keypoints on the image
        drawKeypoints(ctx, keypoints);

        // Create the uploads directory if it doesn't exist
        const uploadsDir = 'public/processed_images';
        if (!fs.existsSync(uploadsDir)) {
            fs.mkdirSync(uploadsDir, { recursive: true });
        }

        // Save the processed image
        const processedImagePath = `${uploadsDir}/${Date.now()}_processed.jpg`;
        const processedImageBuffer = canvas.toBuffer('image/jpeg');
        fs.writeFileSync(processedImagePath, processedImageBuffer);
        logger.info(`Processed image saved at: ${processedImagePath}`);

        return processedImagePath;
    } catch (error) {
        logger.error(`Error adding overlay to image: ${error.message}`);
        throw new Error(`Error adding overlay to image: ${error.message}`);
    }
}

/**
 * Draw keypoints and connections on the given canvas context.
 * @param {object} ctx - The canvas rendering context.
 * @param {Array} keypoints - The keypoints to draw on the canvas.
 */
const drawKeypoints = (ctx, keypoints) => {
    // Validate keypoints
    if (!Array.isArray(keypoints) || keypoints.length === 0) {
        throw new Error('Invalid keypoints data');
    }

    // Draw lines between keypoints
    KEYPOINT_EDGE_INDS_TO_COLOR.forEach(({ start, end, color }) => {
        if (keypoints[start] && keypoints[end]) {
            const [x1, y1] = keypoints[start];
            const [x2, y2] = keypoints[end];
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(x1 * ctx.canvas.width, y1 * ctx.canvas.height);
            ctx.lineTo(x2 * ctx.canvas.width, y2 * ctx.canvas.height);
            ctx.stroke();
        }
    });

    // Draw keypoints
    ctx.fillStyle = 'blue';
    keypoints.forEach(keypoint => {
        if (Array.isArray(keypoint) && keypoint.length >= 2) {
            const [x, y] = keypoint;
            ctx.beginPath();
            ctx.arc(x * ctx.canvas.width, y * ctx.canvas.height, 5, 0, 2 * Math.PI);
            ctx.fill();
        }
    });
}

module.exports = {
    initializeMoveNetModel,
    detectKeypoints,
    addOverlayToImage
}