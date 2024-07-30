const express = require('express');
const logger = require('./middleware/logger');
const webRoutes = require('./routes/web');
const cron = require('node-cron');
const { cleanupUploads, cleanupProcessedImages } = require('./utils/cleanup');
const { initializeMoveNetModel } = require('./movenet/movenet');

// Create new express app
const app = express();
const port = process.env.WEB_PORT || 3000;

// Setup view engine
app.set('view engine', 'ejs');
app.set('views', './src/views');

// Middleware
app.use(express.static('public'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Logging middleware
app.use((req, res, next) => {
    logger.info(`${req.method} ${req.url}`);
    next();
});

// Register routes
app.use('/', webRoutes);

// Schedule the cleanup to run every day at midnight
cron.schedule('0 0 * * *', () => {
    logger.info('Running scheduled cleanup for old images');
    cleanupProcessedImages();
    cleanupUploads();
});

// Initialize MoveNet detector before application started
initializeMoveNetModel()
    .then(detector => {
        // Store the initialized detector in a global variable
        global.detector = detector;

        // Start listening after detector initialized
        app.listen(port, () => {
            logger.info(`Server is running on port ${port}`);
        })

        // Graceful shutdown
        const shutdown = () => {
            logger.info('Received shutdown signal, shutting down gracefully...');
            server.close(err => {
                if (err) {
                    logger.error(`Error during server shutdown: ${err.message}`);
                    process.exit(1);
                }
                logger.info('Server closed successfully');
                process.exit(0);
            });
        };

        process.on('SIGTERM', shutdown);
        process.on('SIGINT', shutdown);
    })
    .catch(err => {
        logger.error(`Error initializing MoveNet detector: ${err.message}`);
        process.exit(1);
    });