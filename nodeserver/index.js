// Node Data Server for Project Nodes

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const fs = require('fs');
const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(bodyParser.json());

const DATA_FILE = './nodes.json';

// Load or initialize node data
function loadNodes() {
  if (fs.existsSync(DATA_FILE)) {
    return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  }
  return [];
}

function saveNodes(nodes) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(nodes, null, 2));
}

// Get all nodes
app.get('/nodes', (req, res) => {
  res.json(loadNodes());
});

// Get a single node by id
app.get('/nodes/:id', (req, res) => {
  const nodes = loadNodes();
  const node = nodes.find(n => n.id === req.params.id);
  if (node) res.json(node);
  else res.status(404).json({ error: 'Node not found' });
});

// Create a new node
app.post('/nodes', (req, res) => {
  const nodes = loadNodes();
  const node = { ...req.body, id: Date.now().toString() };
  nodes.push(node);
  saveNodes(nodes);
  res.status(201).json(node);
});

// Update a node
app.put('/nodes/:id', (req, res) => {
  let nodes = loadNodes();
  const idx = nodes.findIndex(n => n.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Node not found' });
  nodes[idx] = { ...nodes[idx], ...req.body, id: nodes[idx].id };
  saveNodes(nodes);
  res.json(nodes[idx]);
});

// Delete a node
app.delete('/nodes/:id', (req, res) => {
  let nodes = loadNodes();
  const idx = nodes.findIndex(n => n.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Node not found' });
  const deleted = nodes.splice(idx, 1)[0];
  saveNodes(nodes);
  res.json(deleted);
});

app.listen(PORT, () => {
  console.log(`Node Data Server running on port ${PORT}`);
});