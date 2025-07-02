// Entry point for Node.js backend

const express = require('express');
const app = express();
const port = 5000;
const bcrypt = require('bcrypt');
const speakeasy = require('speakeasy');

app.get('/', (req, res) => {
  res.send('Backend is running');
});

// Endpoint for assigning tasks to team members
app.post('/assign-task', async (req, res) => {
  const { teamMemberEmail, task } = req.body;
  try {
    const TeamMember = mongoose.model('TeamMember', teamMemberSchema);
    const teamMember = await TeamMember.findOne({ email: teamMemberEmail });
    if (!teamMember) {
      return res.status(404).send({ message: 'Team member not found' });
    }
    teamMember.tasks = teamMember.tasks || [];
    teamMember.tasks.push(task);
    await teamMember.save();
    res.status(200).send({ message: 'Task assigned successfully', teamMember });
  } catch (error) {
    res.status(500).send({ message: 'Error assigning task', error });
  }
});
// Middleware for checking permissions
function checkPermissions(requiredPermissions) {
  return (req, res, next) => {
    const userPermissions = req.user.permissions || [];
    const hasPermission = requiredPermissions.every(permission => userPermissions.includes(permission));
    if (!hasPermission) {
      return res.status(403).send({ message: 'Access denied' });
    }
    next();
  };
}

// Endpoint for user login
/**
 * User login endpoint with password and optional 2FA
 */
app.post('/login', async (req, res) => {
  const { email, password, twoFACode } = req.body;
  try {
    const TeamMember = mongoose.model('TeamMember', teamMemberSchema);
    const user = await TeamMember.findOne({ email });
    if (!user) {
      return res.status(401).send({ message: 'Invalid credentials' });
    }
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      return res.status(401).send({ message: 'Invalid credentials' });
    }
    if (user.twoFAEnabled) {
      if (!twoFACode) {
        return res.status(401).send({ message: '2FA code required', twoFARequired: true });
      }
      const verified = speakeasy.totp.verify({
        secret: user.twoFASecret,
        encoding: 'base32',
        token: twoFACode
      });
      if (!verified) {
        return res.status(401).send({ message: 'Invalid 2FA code' });
      }
    }
    res.status(200).send({ message: 'Login successful', user: { email: user.email, name: user.name, twoFAEnabled: user.twoFAEnabled } });
  } catch (error) {
    res.status(500).send({ message: 'Error during login', error });
  }
});
// User registration endpoint with password hashing and 2FA secret generation
app.post('/register', async (req, res) => {
  const { name, role, email, password, enable2FA } = req.body;
  try {
    const TeamMember = mongoose.model('TeamMember', teamMemberSchema);
    const existing = await TeamMember.findOne({ email });
    if (existing) {
      return res.status(409).send({ message: 'User already exists' });
    }
    const hashedPassword = await bcrypt.hash(password, 10);
    let twoFASecret = null;
    let twoFAEnabled = false;
    if (enable2FA) {
      twoFASecret = speakeasy.generateSecret({ length: 20 }).base32;
      twoFAEnabled = true;
    }
    const user = new TeamMember({
      name,
      role,
      email,
      password: hashedPassword,
      permissions: [],
      twoFAEnabled,
      twoFASecret
    });
    await user.save();
    res.status(201).send({
      message: 'Registration successful',
      user: { email: user.email, name: user.name, twoFAEnabled: user.twoFAEnabled, twoFASecret: twoFASecret || undefined }
    });
  } catch (error) {
    res.status(500).send({ message: 'Error during registration', error });
  }
});

app.listen(port, () => {
  console.log(`Backend server is listening on port ${port}`);
});
// Database integration
const mongoose = require('mongoose');
mongoose.connect('mongodb://localhost:27017/projectDB', { useNewUrlParser: true, useUnifiedTopology: true });

// Define schemas
// Extend teamMemberSchema to include authentication and permissions
const teamMemberSchema = new mongoose.Schema({
  name: String,
  role: String,
  email: { type: String, unique: true, required: true },
  password: { type: String, required: true },
  permissions: [String], // Array of permissions
  twoFAEnabled: { type: Boolean, default: false },
  twoFASecret: { type: String, default: null }
});

const subTaskSchema = new mongoose.Schema({ name: String, status: String });
const taskSchema = new mongoose.Schema({ name: String, status: String, assignee: { type: String, default: null }, subTasks: [subTaskSchema] });
const projectSchema = new mongoose.Schema({
  name: String,
  teamMembers: [teamMemberSchema],
  deadline: Date,
  tasks: [taskSchema]
});

const Project = mongoose.model('Project', projectSchema);

// Update /create-project endpoint
// DEBUG: Log incoming request for MongoDB create-project
console.log('MongoDB /create-project called. Body:', req.body);
app.post('/create-project', async (req, res) => {
// Assign all unassigned tasks to the first team member by default
if (teamMembers && teamMembers.length > 0 && tasks && tasks.length > 0) {
  tasks.forEach(task => {
    if (!task.assignee) {
      task.assignee = teamMembers[0].name;
    }
  });
}
  try {
    const { name, teamMembers, deadline, tasks } = req.body;
    const newProject = new Project({ name, teamMembers, deadline, tasks });
    await newProject.save();
    res.status(201).send({ message: 'Project created successfully', project: newProject });
  } catch (error) {
    res.status(500).send({ message: 'Error creating project', error });
  }
// Endpoint to assign/reassign a task's assignee in a project
app.post('/assign-task-to-member', async (req, res) => {
  const { projectId, taskId, assignee } = req.body;
// DEBUG: Log incoming request for in-memory create-project
console.log('In-memory /create-project called. Body:', req.body);
  try {
    const project = await Project.findById(projectId);
    if (!project) {
      return res.status(404).send({ message: 'Project not found' });
    }
    const task = project.tasks.id(taskId);
    if (!task) {
      return res.status(404).send({ message: 'Task not found' });
    }
    task.assignee = assignee || null;
    await project.save();
    res.status(200).send({ message: 'Task assignment updated', task });
  } catch (error) {
    res.status(500).send({ message: 'Error updating task assignment', error });
  }
});
});
// Feature: Creating projects

const projects = [];

app.post('/create-project', (req, res) => {
  const { name, teamMembers, deadline, tasks } = req.body;

  const newProject = {
    id: projects.length + 1,
    name,
    teamMembers,
    deadline,
    tasks: tasks.map(task => ({
      ...task,
      assignee: task.assignee || null,
      subTasks: task.subTasks || []
    }))
  };

  projects.push(newProject);
  res.status(201).send({ message: 'Project created successfully', project: newProject });
});