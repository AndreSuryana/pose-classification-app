const express = require('express');
const logger = require('./middleware/logger');
const webRoutes = require('./routes/web');

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

// Start listening
app.listen(port, () => {
    logger.info(`Server is running on port ${port}`);
})