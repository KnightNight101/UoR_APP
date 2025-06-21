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