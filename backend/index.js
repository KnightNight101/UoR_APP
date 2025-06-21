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
// Database integration
const mongoose = require('mongoose');
mongoose.connect('mongodb://localhost:27017/projectDB', { useNewUrlParser: true, useUnifiedTopology: true });

// Define schemas
const teamMemberSchema = new mongoose.Schema({ name: String, role: String });
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