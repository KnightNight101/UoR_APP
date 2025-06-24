// Entry point for React.js application

import React, { useState } from 'react';
import ReactDOM from 'react-dom';

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
          <li key={index}>
            {task.name} - {task.status} - {task.assignee ? task.assignee : 'unassigned'}
          </li>
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
  { name: 'Subtask 1', status: 'Pending', assignee: null },
  { name: 'Subtask 2', status: 'Completed', assignee: 'Alice' }
];

const exampleProjects = [
  { name: 'Project A' },
  { name: 'Project B' }
];

// Only render CreateProject for debugging and feature validation
function CreateProject() {
  const [project, setProject] = useState({
    name: '',
    teamMembers: [],
    deadline: '',
    tasks: []
  });

  const [currentTask, setCurrentTask] = useState({ name: '', status: 'Pending', assignee: '', subTasks: [] });

  const handleAddTask = () => {
    console.log('Adding task:', currentTask);
    setProject({ ...project, tasks: [...project.tasks, { ...currentTask, assignee: currentTask.assignee || null }] });
    setCurrentTask({ name: '', status: 'Pending', assignee: '', subTasks: [] });
  };

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

  // DEBUG: CreateProject form rendered
  console.log('CreateProject form rendered');

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Project Name"
        value={project.name}
        onChange={(e) => setProject({ ...project, name: e.target.value })}
      />
      {/* Inputs for team members */}
      <input
        type="text"
        placeholder="Team Member Name"
        onChange={(e) => {
          const newMember = { name: e.target.value, role: '' };
          setProject(prev => {
            const updatedMembers = [...prev.teamMembers, newMember];
            // If this is the first member, set currentTask.assignee to their name
            if (updatedMembers.length === 1) {
              setCurrentTask(ct => ({ ...ct, assignee: newMember.name }));
            }
            return { ...prev, teamMembers: updatedMembers };
          });
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

      {/* Input for deadline */}
      <input
        type="date"
        value={project.deadline}
        onChange={(e) => setProject({ ...project, deadline: e.target.value })}
      />

      {/* Inputs for tasks and subtasks */}
      <input
        type="text"
        placeholder="Task Name"
        value={currentTask.name}
        onChange={(e) => setCurrentTask({ ...currentTask, name: e.target.value })}
      />
      <input
        type="text"
        placeholder="Assignee (optional)"
        value={currentTask.assignee}
        onChange={(e) => setCurrentTask({ ...currentTask, assignee: e.target.value })}
      />
      <button type="button" onClick={handleAddTask}>Add Task</button>

      {/* List current tasks */}
      <ul>
        {project.tasks.map((task, idx) => (
          <li key={idx}>
            {task.name} - {task.status} - {task.assignee ? task.assignee : 'unassigned'}
          </li>
        ))}
      </ul>

      <button type="submit">Create Project</button>
    </form>
  );
}

// ProjectDetails component for assigning/reassigning tasks and adding tasks/team members
function ProjectDetails({ project }) {
  const [tasks, setTasks] = React.useState(project.tasks);
  const [teamMembers, setTeamMembers] = React.useState(project.teamMembers);

  const handleAssigneeChange = async (taskId, newAssignee) => {
    const response = await fetch('/assign-task-to-member', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ projectId: project._id || project.id, taskId, assignee: newAssignee })
    });
    const data = await response.json();
    if (response.ok) {
      setTasks(tasks.map(task =>
        (task._id === taskId || task.id === taskId)
          ? { ...task, assignee: newAssignee }
          : task
      ));
    } else {
      alert(data.message || 'Failed to update assignee');
    }
  };

  const handleAddTask = () => {
    const name = prompt('Enter task name:');
    if (name) {
      setTasks(prev => [...prev, { name, status: 'Pending', assignee: '', subTasks: [] }]);
    }
  };

  const handleAddTeamMember = () => {
    const name = prompt('Enter team member name:');
    const role = prompt('Enter team member role:');
    if (name) {
      setTeamMembers(prev => [...prev, { name, role }]);
    }
  };

  return (
    <div>
      <h2>{project.name} - Project Page</h2>
      <h3>Tasks</h3>
      <ul>
        {tasks.map((task) => (
          <li key={task._id || task.id}>
            {task.name} - {task.status} - 
            <select
              value={task.assignee || ''}
              onChange={e => handleAssigneeChange(task._id || task.id, e.target.value)}
            >
              <option value="">unassigned</option>
              {teamMembers.map((member, idx) => (
                <option key={idx} value={member.name}>{member.name}</option>
              ))}
            </select>
          </li>
        ))}
      </ul>
      <button type="button" onClick={handleAddTask}>Add Task</button>
      <h3>Team Members</h3>
      <ul>
<div style={{color: 'red', fontWeight: 'bold'}}>DEBUG: ProjectDetails component is rendered</div>
      {console.log('DEBUG: ProjectDetails component is rendered')}
        {teamMembers.map((member, idx) => (
          <li key={idx}>{member.name} - {member.role}</li>
        ))}
      </ul>
      <button type="button" onClick={handleAddTeamMember}>Add Team Member</button>
    </div>
  );
}

// Render ProjectDetails with a sample project for testing
const sampleProject = {
  name: 'Sample Project',
  teamMembers: [{ name: 'Alice', role: 'Developer' }],
  tasks: [{ name: 'Initial Task', status: 'Pending', assignee: 'Alice', subTasks: [] }]
};
ReactDOM.render(<ProjectDetails project={sampleProject} />, document.getElementById('root'));