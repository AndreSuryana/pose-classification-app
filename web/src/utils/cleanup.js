const fs = require('fs');
const path = require('path');
const logger = require('../middleware/logger');
const config = require('../config');

// Function to delete all files in a directory
const deleteAllFiles = (directory) => {
    fs.readdir(directory, (err, files) => {
        if (err) {
            logger.error(`Error reading directory ${directory}: ${err.message}`);
            return;
        }

        files.forEach(file => {
            const filePath = path.join(directory, file);
            fs.unlink(filePath, (err) => {
                if (err) {
                    logger.error(`Error deleting file ${filePath}: ${err.message}`);
                } else {
                    logger.debug(`Deleted file: ${filePath}`);
                }
            });
        });
    });
};

// Cleanup uploads directory
const cleanupUploads = () => {
    const uploadsDir = path.join(__dirname, '../../public/uploads');
    deleteAllFiles(uploadsDir);
};

// Cleanup processed images directory
const cleanupProcessedImages = () => {
    const processedImagesDir = path.join(__dirname, '../../public/processed_images');
    deleteAllFiles(processedImagesDir);
};

module.exports = {
    cleanupUploads,
    cleanupProcessedImages
};