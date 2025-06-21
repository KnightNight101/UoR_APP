// Entry point for Node.js backend

const express = require('express');
const app = express();
const port = 5000;

app.get('/', (req, res) => {
  res.send('Backend is running');
});

app.listen(port, () => {
  console.log(`Backend server is listening on port ${port}`);
});