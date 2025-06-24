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
function MainPage({ tasks, projects }) {
  const [showCreate, setShowCreate] = useState(false);
  const [showLogin, setShowLogin] = useState(false);

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
          </>
        ) : (
          <CreateProject onBack={() => setShowCreate(false)} />
        )}
      </div>
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

// Feature: Creating projects UI
function CreateProject({ onBack }) {
  const [project, setProject] = useState({
    name: '',
    teamMembers: [],
    deadline: '',
    tasks: []
  });
  const [currentTaskName, setCurrentTaskName] = useState('');
  const [currentSubTaskName, setCurrentSubTaskName] = useState('');
  const [draggedSubTaskIdx, setDraggedSubTaskIdx] = useState(null);

  // Add a new task
  const addTask = () => {
    if (currentTaskName.trim() === '') return;
    setProject({
      ...project,
      tasks: [
        ...project.tasks,
        { name: currentTaskName, status: 'Pending', subTasks: [] }
      ]
    });
    setCurrentTaskName('');
  };

  // Add a new subtask to the last task
  const addSubTask = (taskIdx) => {
    if (currentSubTaskName.trim() === '') return;
    const updatedTasks = [...project.tasks];
    updatedTasks[taskIdx].subTasks.push({ name: currentSubTaskName, status: 'Pending' });
    setProject({ ...project, tasks: updatedTasks });
    setCurrentSubTaskName('');
  };

  // Drag and drop handlers for subtasks
  const handleDragStart = (taskIdx, subIdx) => {
    setDraggedSubTaskIdx({ taskIdx, subIdx });
  };

  const handleDrop = (taskIdx, subIdx) => {
    if (!draggedSubTaskIdx || draggedSubTaskIdx.taskIdx !== taskIdx) return;
    const updatedTasks = [...project.tasks];
    const subTasks = [...updatedTasks[taskIdx].subTasks];
    const [removed] = subTasks.splice(draggedSubTaskIdx.subIdx, 1);
    subTasks.splice(subIdx, 0, removed);
    updatedTasks[taskIdx].subTasks = subTasks;
    setProject({ ...project, tasks: updatedTasks });
    setDraggedSubTaskIdx(null);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  // Set subtask status
  const setSubTaskStatus = (taskIdx, subIdx, status) => {
    const updatedTasks = [...project.tasks];
    updatedTasks[taskIdx].subTasks[subIdx].status = status;
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
      {/* Inputs for team members */}
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
          if (updatedMembers.length > 0) {
            updatedMembers[updatedMembers.length - 1].role = e.target.value;
            setProject({ ...project, teamMembers: updatedMembers });
          }
        }}
      />
      {/* Input for deadline */}
      <input
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
        <button type="button" onClick={addTask}>Add Task</button>
      </div>
      {/* List of tasks and subtasks */}
      {project.tasks.map((task, taskIdx) => (
        <div key={taskIdx} style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '1rem' }}>
          <strong>{task.name} ({task.status})</strong>
          <div style={{ marginTop: '0.5rem', marginBottom: '0.5rem' }}>
            <label>Status: </label>
            <select
              value={task.status}
              onChange={e => {
                const updatedTasks = [...project.tasks];
                updatedTasks[taskIdx].status = e.target.value;
                setProject({ ...project, tasks: updatedTasks });
              }}
            >
              <option value="Pending">Pending</option>
              <option value="In Progress">In Progress</option>
              <option value="Completed">Completed</option>
            </select>
          </div>
          {/* Subtasks */}
          <div>
            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
              <input
                type="text"
                placeholder="Subtask Name"
                value={currentSubTaskName}
                onChange={e => setCurrentSubTaskName(e.target.value)}
              />
              <button type="button" onClick={() => addSubTask(taskIdx)}>Add Subtask</button>
            </div>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {task.subTasks.map((sub, subIdx) => (
                <li
                  key={subIdx}
                  draggable
                  onDragStart={() => handleDragStart(taskIdx, subIdx)}
                  onDragOver={handleDragOver}
                  onDrop={() => handleDrop(taskIdx, subIdx)}
                  style={{
                    background: '#f9f9f9',
                    margin: '0.25rem 0',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    display: 'flex',
                    alignItems: 'center',
                    cursor: 'grab'
                  }}
                >
                  <span style={{ flex: 1 }}>{sub.name} ({sub.status})</span>
                  <select
                    value={sub.status}
                    onChange={e => setSubTaskStatus(taskIdx, subIdx, e.target.value)}
                  >
                    <option value="Pending">Pending</option>
                    <option value="In Progress">In Progress</option>
                    <option value="Completed">Completed</option>
                  </select>
                  <span style={{ marginLeft: '0.5rem', cursor: 'grab' }}>⠿</span>
                </li>
              ))}
            </ul>
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