// Entry point for Node.js backend

const express = require('express');
const app = express();
const port = 5000;

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
app.post('/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const user = await mongoose.model('TeamMember', teamMemberSchema).findOne({ email });
    if (!user || user.password !== password) {
      return res.status(401).send({ message: 'Invalid credentials' });
    }
    res.status(200).send({ message: 'Login successful', user });
  } catch (error) {
    res.status(500).send({ message: 'Error during login', error });
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
  permissions: [String] // Array of permissions
});

const subTaskSchema = new mongoose.Schema({ name: String, status: String });
const taskSchema = new mongoose.Schema({ name: String, status: String, subTasks: [subTaskSchema] });
const projectSchema = new mongoose.Schema({
  name: String,
  teamMembers: [teamMemberSchema],
  deadline: Date,
  tasks: [taskSchema]
});

const Project = mongoose.model('Project', projectSchema);

// Update /create-project endpoint
app.post('/create-project', async (req, res) => {
  try {
    const { name, teamMembers, deadline, tasks } = req.body;
    const newProject = new Project({ name, teamMembers, deadline, tasks });
    await newProject.save();
    res.status(201).send({ message: 'Project created successfully', project: newProject });
  } catch (error) {
    res.status(500).send({ message: 'Error creating project', error });
  }
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
      subTasks: task.subTasks || []
    }))
  };

  projects.push(newProject);
  res.status(201).send({ message: 'Project created successfully', project: newProject });
});