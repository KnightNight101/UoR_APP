# Local Run Setup

This directory contains all files needed to run the backend, frontend, and deepseek_r1 features without containerisation.

## Backend

- index.js
- package.json
- package-lock.json

## Frontend

- src/index.js
- package.json
- package-lock.json

## deepseek_r1

- config.json

## How to Run

1. Install dependencies for backend and frontend:
   ```
   cd backend
   npm install
   cd ../frontend
   npm install
   ```

2. Start backend:
   ```
   cd backend
   npm start
   ```

3. Start frontend:
   ```
   cd frontend
   npm start
   ```

4. Use `deepseek_r1/config.json` as needed by your application.