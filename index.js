const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

// Routes
app.get('/', (req, res) => {
  res.send('Financial Scanner is Running!');
});

app.get('/scan', (req, res) => {
  res.json({ message: 'Scanning financial data...' });
});

// Start server
app.listen(PORT, () => {
  console.log(Financial Scanner running on port ${PORT});
});
