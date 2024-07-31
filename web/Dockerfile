# Official Node.js image as base image
FROM node:20.14.0-slim

# Install PM2 globally
RUN npm install -g pm2

WORKDIR /web

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install the project dependencies
RUN npm install
# RUN npm ci

# Copy the rest of the project files to the working directory
COPY . .

# Expose the port the app runs on
EXPOSE ${WEB_PORT}

# Define the command to run the application using PM2
CMD ["pm2-runtime", "start", "pm2.config.js"]

# Define the command to run the application
# CMD [ "npm", "run", "start" ]