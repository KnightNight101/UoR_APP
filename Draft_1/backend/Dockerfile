# Base image for Node.js
FROM node:16

# Debugging: Log current directory contents
RUN ls -la /app
# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Start the application
CMD ["npm", "start"]