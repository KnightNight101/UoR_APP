// Node Data Server for Project Nodes

const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const fs = require('fs');
const app = express();
const PORT = process.env.PORT || 4000;

app.use(cors());
app.use(bodyParser.json());

// Single permissive CSP middleware before static
app.use((req, res, next) => {
  res.setHeader(
    "Content-Security-Policy",
    "default-src *; script-src * 'unsafe-inline' 'unsafe-eval'; style-src * 'unsafe-inline'; img-src * data:; connect-src *;"
  );
  next();
});


const DATA_FILE = './nodes.json';

// In-memory mock data for UI
let members = [
  { id: '1', name: 'Alice', role: 'Developer' },
  { id: '2', name: 'Bob', role: 'Manager' }
];
let projects = [
  { id: 'p1', name: 'Project Alpha' },
  { id: 'p2', name: 'Project Beta' }
];
let eventLog = [
  { time: new Date().toLocaleString(), message: 'Server started' }
];

// --- Simple Auth Middleware ---
function requireAuth(req, res, next) {
  if (
    req.path.startsWith("/auth/") ||
    req.method === "OPTIONS"
  ) return next();
  const token = req.headers.authorization || req.headers.Authorization;
  if (token === "Bearer demo-token") return next();
  res.status(401).json({ error: "Unauthorized" });
}
app.use(requireAuth);
// --- Simple Auth (file-based, plaintext for demo) ---
const USERS_FILE = './users.json';
function loadUsers() {
  if (fs.existsSync(USERS_FILE)) {
    return JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));
  }
  return [];
}
function saveUsers(users) {
  fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
}

// Register
app.post('/auth/register', (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) return res.status(400).json({ error: 'Missing username or password' });
  let users = loadUsers();
  if (users.find(u => u.username === username)) return res.status(409).json({ error: 'User exists' });
  users.push({ username, password });
  saveUsers(users);
  res.json({ success: true });
});

// Login
app.post('/auth/login', (req, res) => {
  const { username, password } = req.body;
  let users = loadUsers();
  const user = users.find(u => u.username === username && u.password === password);
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });
  // For demo: return a fake token
  res.json({ token: 'demo-token', username });
});
// Event log helper
// List all registered users (for admin UI)
app.get('/users', (req, res) => {
  const users = loadUsers().map(u => ({ username: u.username }));
  res.json(users);
});
function logEvent(msg) {
  eventLog.unshift({ time: new Date().toLocaleString(), message: msg });
  if (eventLog.length > 100) eventLog.pop();
}

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
  logEvent('Fetched all nodes');
  res.json(loadNodes());
});

// --- Admin UI endpoints ---
app.get('/members', (req, res) => {
  logEvent('Fetched members');
  res.json(members);
});

app.get('/projects', (req, res) => {
  logEvent('Fetched projects');
  res.json(projects);
});

app.get('/logs', (req, res) => {
  res.json(eventLog);
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
  logEvent('Created node ' + node.id);
  res.status(201).json(node);
});

// Update a node
app.put('/nodes/:id', (req, res) => {
  let nodes = loadNodes();
  const idx = nodes.findIndex(n => n.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Node not found' });
  nodes[idx] = { ...nodes[idx], ...req.body, id: nodes[idx].id };
  saveNodes(nodes);
  logEvent('Updated node ' + req.params.id);
  res.json(nodes[idx]);
});

// Delete a node
app.delete('/nodes/:id', (req, res) => {
  let nodes = loadNodes();
  const idx = nodes.findIndex(n => n.id === req.params.id);
  if (idx === -1) return res.status(404).json({ error: 'Node not found' });
  const deleted = nodes.splice(idx, 1)[0];
  saveNodes(nodes);
  logEvent('Deleted node ' + req.params.id);
  res.json(deleted);
});

app.use(express.static('public', {
  extensions: ['js', 'html', 'css', 'ico'],
  setHeaders: (res, path) => {
    if (path.endsWith('.js')) {
      res.setHeader('Content-Type', 'application/javascript');
    }
  }
}));

app.listen(PORT, () => {
  logEvent('Node Data Server running on port ' + PORT);
  console.log(`Node Data Server running on port ${PORT}`);
});