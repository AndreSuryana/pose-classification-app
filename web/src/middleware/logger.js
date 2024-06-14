const { createLogger, format, transports } = require('winston');
require('winston-daily-rotate-file');

// Get log level from environment variables
const getLoggerLevel = () => {
    switch (process.env.LOG_LEVEL) {
        case 'debug':
        case 'all':
            return 'debug';
        case 'error':
            return 'error';
        default:
            return 'info';
    }
};

// Custom log format
const logFormat = format.printf(({ level, message, timestamp }) => {
    return `${timestamp} [${level.toUpperCase()}]: ${message}`;
});

// Create the logger
const logger = createLogger({
    level: getLoggerLevel(),
    format: format.combine(
        format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
        logFormat,
    ),
    transports: [
        new transports.Console(),
        new transports.DailyRotateFile({
            filename: 'logs/app-%DATE%.log',
            datePattern: 'YYYY-MM-DD',
            maxFiles: '14d' // Keep logs for 2 weeks,
        }),
        new transports.File({ filename: 'logs/error/error.log', level: 'error' }),
    ]
});

module.exports = logger;