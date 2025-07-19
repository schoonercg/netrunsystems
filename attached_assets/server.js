// Entry point of the Netrun Systems application
const express = require('express');
const app = express();
const port = process.env.PORT || 3000;

app.get('/', (req, res) => {
  res.send('Netrun Systems Backend');
});

app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
const path = require('path');

// Serve static files from the React frontend app
app.use(express.static(path.join(__dirname, 'client/build')));

// Anything that doesn't match the above, send back the index.html file
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname + '/client/build/index.html'));
});
