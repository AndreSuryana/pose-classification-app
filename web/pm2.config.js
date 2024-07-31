module.exports = {
    apps: [
        {
            name: 'pose-classification-web',
            script: './src/app.js',
            watch: true,
            ignore_watch: ['logs', 'node_modules'],
            autorestart: true,
            max_memory_restart: '400M',
            env: {
                NODE_ENV: process.env.APP_ENV || 'development',
                WEB_PORT: process.env.WEB_PORT || 3000
            },
            env_production: {
                NODE_ENV: process.env.APP_ENV || 'production',
                WEB_PORT: process.env.WEB_PORT || 3000
            }
        }
    ]
};