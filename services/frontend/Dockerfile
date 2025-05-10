# Base Node.js image
FROM node:18-alpine

# Set working directory in the container
WORKDIR /usr/src/clothing-store/frontend

# Copy package.json and package-lock.json for dependency installation
COPY package*.json ./

# Install all dependencies, including dev dependencies
RUN npm install

# Copy all application code
COPY . .
