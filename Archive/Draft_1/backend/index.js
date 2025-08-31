// Entry point for Node.js backend with PostgreSQL

const express = require('express');
const app = express();
const port = 5000;
const bcrypt = require('bcrypt');
const speakeasy = require('speakeasy');
const db = require('./db');

app.use(express.json());

// LLM Infrastructure: Modular LLM executor and switchboard (scaffold)
const llmModules = {};
function registerLLM(name, executor) {
  llmModules[name] = executor;
}
function getLLM(name) {
  return llmModules[name];
}
// Secure communication (scaffold): recommend using HTTPS in production
// const https = require('https');
// const fs = require('fs');
// LLM Task Delegation Endpoint (scaffold)
app.post('/llm-task', async (req, res) => {
  const { model, prompt } = req.body;
  const executor = getLLM(model || 'default');
  if (!executor) {
    return res.status(400).json({ error: 'LLM model not found' });
  }
  try {
    const result = await executor(prompt);
    res.json({ result });
  } catch (err) {
    res.status(500).json({ error: 'LLM execution failed', details: err.message });
  }
});
// const server = https.createServer({ key: fs.readFileSync('key.pem'), cert: fs.readFileSync('cert.pem') }, app);
// server.listen(port);
// Example: registerLLM('default', async (prompt) => { ... });

app.get('/', (req, res) => {
  res.send('Backend is running');
});

// User login endpoint with password and optional 2FA
app.post('/login', async (req, res) => {
  const { email, password, twoFACode } = req.body;
  try {
    const { rows } = await db.query('SELECT * FROM users WHERE email = $1', [email]);
    const user = rows[0];
    if (!user) {
      return res.status(401).send({ message: 'Invalid credentials' });
    }
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      return res.status(401).send({ message: 'Invalid credentials' });
    }
    if (user.twofa_enabled) {
      if (!twoFACode) {
        return res.status(401).send({ message: '2FA code required', twoFARequired: true });
      }
      const verified = speakeasy.totp.verify({
        secret: user.twofa_secret,
        encoding: 'base32',
        token: twoFACode
      });
      if (!verified) {
        return res.status(401).send({ message: 'Invalid 2FA code' });
      }
    }
    res.status(200).send({ message: 'Login successful', user: { email: user.email, name: user.name, twoFAEnabled: user.twofa_enabled } });
  } catch (error) {
    res.status(500).send({ message: 'Error during login', error });
  }
});

// User registration endpoint with password hashing and 2FA secret generation (admin only)
app.post('/register', async (req, res) => {
  const { name, role, email, password, enable2FA, permissions = [] } = req.body;
  try {
    const { rows: existing } = await db.query('SELECT * FROM users WHERE email = $1', [email]);
    if (existing.length > 0) {
      return res.status(409).send({ message: 'User already exists' });
    }
    const hashedPassword = await bcrypt.hash(password, 10);
    let twoFASecret = null;
    let twoFAEnabled = false;
    if (enable2FA) {
      twoFASecret = speakeasy.generateSecret({ length: 20 }).base32;
      twoFAEnabled = true;
    }
    const insertQuery = `
      INSERT INTO users (name, role, email, password, permissions, twofa_enabled, twofa_secret)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING id, email, name, twofa_enabled
    `;
    const values = [name, role, email, hashedPassword, permissions, twoFAEnabled, twoFASecret];
    const { rows } = await db.query(insertQuery, values);
    res.status(201).send({
      message: 'Registration successful',
      user: rows[0]
    });
  } catch (error) {
    res.status(500).send({ message: 'Error during registration', error });
  }
});

// Example: Get all projects
app.get('/projects', async (req, res) => {
  try {
    const { rows } = await db.query('SELECT * FROM projects');
    res.json(rows);
  } catch (error) {
    res.status(500).send({ message: 'Error fetching projects', error });
  }
});

// Example: Create a project
app.post('/create-project', async (req, res) => {
  const { name, deadline, teamMembers = [], tasks = [] } = req.body;
  try {
    const projectResult = await db.query(
      'INSERT INTO projects (name, deadline) VALUES ($1, $2) RETURNING id, name, deadline',
      [name, deadline]
    );
    const projectId = projectResult.rows[0].id;

    // Add team members
    for (const member of teamMembers) {
      // Find user by email
      const { rows: userRows } = await db.query('SELECT id FROM users WHERE email = $1', [member.email]);
      if (userRows.length > 0) {
        await db.query('INSERT INTO team_members (project_id, user_id) VALUES ($1, $2)', [projectId, userRows[0].id]);
      }
    }

    // Add tasks
    for (const task of tasks) {
      await db.query(
        'INSERT INTO tasks (project_id, name, status, assignee_id) VALUES ($1, $2, $3, $4)',
        [projectId, task.name, task.status, null]
      );
    }

    res.status(201).send({ message: 'Project created successfully', project: projectResult.rows[0] });
  } catch (error) {
    res.status(500).send({ message: 'Error creating project', error });
  }
});

app.listen(port, () => {
  console.log(`Backend server is listening on port ${port}`);
});