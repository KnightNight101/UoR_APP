import React, { useState } from 'react';
import ReactDOM from 'react-dom';

// LoginPage component
function LoginPage({ onBack }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    alert(`Logged in as ${username}`);
    if (onBack) onBack();
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center'
    }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', minWidth: 300 }}>
        <h2>Login</h2>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <div style={{ display: 'flex', gap: '1rem' }}>
          <button type="submit">Login</button>
          <button type="button" onClick={onBack}>Cancel</button>
        </div>
      </form>
    </div>
  );
}

// MainPage component for displaying tasks and projects
function MainPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);

  if (showLogin) {
    return <LoginPage onBack={() => setShowLogin(false)} />;
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top-right menu */}
      <div style={{ position: 'absolute', top: 0, right: 0 }}>
        <button onClick={() => setShowLogin(true)}>Login</button>
        <button>System Settings</button>
        <button>Other Features</button>
      </div>

      {/* Centered content */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center'
      }}>
        {!showCreate ? (
          <>
            <button
              style={{
                padding: '1rem 2rem',
                fontSize: '1.5rem',
                marginBottom: '2rem',
                cursor: 'pointer'
              }}
              onClick={() => setShowCreate(true)}
            >
              New project
            </button>
            <h1>Today's To-Do List</h1>
            <ul>
              {tasks.length === 0 ? <li>No tasks</li> : tasks.map((task, index) => (
                <li key={index}>{task.name} - {task.status}</li>
              ))}
            </ul>
            <h1>Projects</h1>
            <ul>
              {projects.length === 0 ? <li>No projects</li> : projects.map((project, index) => (
                <li key={index}>{project.name}</li>
              ))}
            </ul>
          </>
        ) : (
          <CreateProject onBack={() => setShowCreate(false)} />
        )}
      </div>
    </div>
  );
}

ReactDOM.render(<MainPage />, document.getElementById('root'));

// Feature: Creating projects UI
function CreateProject({ onBack }) {
  const [project, setProject] = useState({
    name: '',
    teamMembers: [],
    deadline: '',
    tasks: []
  });
  const [currentTeamMember, setCurrentTeamMember] = useState({ name: '', role: '' });
  const [currentTaskName, setCurrentTaskName] = useState('');
  const [currentTaskAssignee, setCurrentTaskAssignee] = useState('');
  const [draggedSubTaskIdx] = useState(null); // Not used anymore

  // Add a new team member
  const addTeamMember = () => {
    if (currentTeamMember.name.trim() === '' || currentTeamMember.role.trim() === '') return;
    setProject({
      ...project,
      teamMembers: [...project.teamMembers, { ...currentTeamMember }]
    });
    setCurrentTeamMember({ name: '', role: '' });
  };

  // Add a new task
  const addTask = () => {
    if (currentTaskName.trim() === '' || currentTaskAssignee === '') return;
    setProject({
      ...project,
      tasks: [
        ...project.tasks,
        { name: currentTaskName, status: 'Pending', assignee: currentTaskAssignee }
      ]
    });
    setCurrentTaskName('');
    setCurrentTaskAssignee('');
  };

  // Set task status
  const setTaskStatus = (taskIdx, status) => {
    const updatedTasks = [...project.tasks];
    updatedTasks[taskIdx].status = status;
    setProject({ ...project, tasks: updatedTasks });
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
    if (onBack) onBack();
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', minWidth: 300 }}>
      <input
        type="text"
        placeholder="Project Name"
        value={project.name}
        onChange={(e) => setProject({ ...project, name: e.target.value })}
        required
      />
      {/* Team Members */}
      <div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.5rem' }}>
          <input
            type="text"
            placeholder="Team Member Name"
            value={currentTeamMember.name}
            onChange={e => setCurrentTeamMember({ ...currentTeamMember, name: e.target.value })}
          />
          <input
            type="text"
            placeholder="Role"
            value={currentTeamMember.role}
            onChange={e => setCurrentTeamMember({ ...currentTeamMember, role: e.target.value })}
          />
          <button type="button" onClick={addTeamMember}>Add Team Member</button>
        </div>
        <ul>
          {project.teamMembers.map((member, idx) => (
            <li key={idx}>{member.name} - {member.role}</li>
          ))}
        </ul>
      </div>
      {/* Project Deadline */}
      <label htmlFor="project-deadline"><strong>Project Deadline</strong></label>
      <input
        id="project-deadline"
        type="date"
        value={project.deadline}
        onChange={(e) => setProject({ ...project, deadline: e.target.value })}
      />
      {/* Task creation */}
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <input
          type="text"
          placeholder="Task Name"
          value={currentTaskName}
          onChange={(e) => setCurrentTaskName(e.target.value)}
        />
        <select
          value={currentTaskAssignee}
          onChange={e => setCurrentTaskAssignee(e.target.value)}
        >
          <option value="">Assign to...</option>
          {project.teamMembers.map((member, idx) => (
            <option key={idx} value={member.name}>{member.name}</option>
          ))}
        </select>
        <button type="button" onClick={addTask}>Add Task</button>
      </div>
      {/* List of tasks */}
      {project.tasks.map((task, taskIdx) => (
        <div key={taskIdx} style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '1rem' }}>
          <strong>{task.name} ({task.status})</strong>
          <div style={{ marginTop: '0.5rem', marginBottom: '0.5rem' }}>
            <label>Status: </label>
            <select
              value={task.status}
              onChange={e => setTaskStatus(taskIdx, e.target.value)}
            >
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="Completed">Completed</option>
            </select>
          </div>
          <div>
            <span>Assigned to: {task.assignee}</span>
          </div>
        </div>
      ))}
      <div style={{ display: 'flex', gap: '1rem' }}>
        <button type="submit">Create Project</button>
        <button type="button" onClick={onBack}>Cancel</button>
      </div>
    </form>
  );
}

export default CreateProject;