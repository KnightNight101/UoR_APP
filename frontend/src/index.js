// Entry point for React.js application

import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

// MainPage component for displaying tasks and projects
function MainPage({ tasks, projects }) {
  return (
    <div>
      {/* Top-right menu */}
      <div style={{ position: 'absolute', top: 0, right: 0 }}>
        <button>Login</button>
        <button>System Settings</button>
        <button>Other Features</button>
      </div>

      {/* Main content */}
      <h1>Tasks</h1>
      <ul>
        {tasks.map((task, index) => (
          <li key={index}>{task.name} - {task.status}</li>
        ))}
      </ul>

      <h1>Projects</h1>
      <ul>
        {projects.map((project, index) => (
          <li key={index}>{project.name}</li>
        ))}
      </ul>
    </div>
  );
}

// Example usage of MainPage
const exampleTasks = [
  { name: 'Subtask 1', status: 'Pending' },
  { name: 'Subtask 2', status: 'Completed' }
];

const exampleProjects = [
  { name: 'Project A' },
  { name: 'Project B' }
];

ReactDOM.render(<MainPage tasks={exampleTasks} projects={exampleProjects} />, document.getElementById('root'));
ReactDOM.render(<App />, document.getElementById('root'));
// Feature: Creating projects UI

import React, { useState } from 'react';

function CreateProject() {
  const [project, setProject] = useState({
    name: '',
    teamMembers: [],
    deadline: '',
    tasks: []
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch('/create-project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(project)
    });
    const data = await response.json();
    alert(data.message);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Project Name"
        onChange={(e) => setProject({ ...project, name: e.target.value })}
      />
// Inputs for team members
<input
  type="text"
  placeholder="Team Member Name"
  onChange={(e) => {
    const newMember = { name: e.target.value, role: '' };
    setProject({ ...project, teamMembers: [...project.teamMembers, newMember] });
  }}
/>
<input
  type="text"
  placeholder="Team Member Role"
  onChange={(e) => {
    const updatedMembers = [...project.teamMembers];
    updatedMembers[updatedMembers.length - 1].role = e.target.value;
    setProject({ ...project, teamMembers: updatedMembers });
  }}
/>

// Input for deadline
<input
  type="date"
  onChange={(e) => setProject({ ...project, deadline: e.target.value })}
/>

// Inputs for tasks and subtasks
<input
  type="text"
  placeholder="Task Name"
  onChange={(e) => {
    const newTask = { name: e.target.value, status: 'Pending', subTasks: [] };
    setProject({ ...project, tasks: [...project.tasks, newTask] });
  }}
/>
<input
  type="text"
  placeholder="Subtask Name"
  onChange={(e) => {
    const updatedTasks = [...project.tasks];
    updatedTasks[updatedTasks.length - 1].subTasks.push({ name: e.target.value, status: 'Pending' });
    setProject({ ...project, tasks: updatedTasks });
  }}
/>
      {/* Add inputs for team members, deadline, tasks */}
      <button type="submit">Create Project</button>
    </form>
  );
}

export default CreateProject;