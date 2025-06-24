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

// ProjectPage component
function ProjectPage({ project, onBack }) {
  return (
    <div style={{ minHeight: '100vh', position: 'relative' }}>
      <div style={{ position: 'absolute', top: 20, left: 20 }}>
        <h2>{project.name}</h2>
        <div style={{ marginTop: '0.5rem', fontWeight: 'bold' }}>
          {project.deadline
            ? <>Deadline: {project.deadline}</>
            : <>No Deadline Specified</>}
        </div>
      </div>
      <div style={{ position: 'absolute', top: 20, right: 20 }}>
        <button onClick={onBack}>Back to Home</button>
      </div>
      {/* Additional project details can be added here */}
    </div>
  );
}

// MainPage component for displaying tasks and projects
function MainPage() {
  const [showCreate, setShowCreate] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [currentProject, setCurrentProject] = useState(null);

  if (showLogin) {
    return <LoginPage onBack={() => setShowLogin(false)} />;
  }

  if (currentProject) {
    return <ProjectPage project={currentProject} onBack={() => setCurrentProject(null)} />;
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
              {tasks.map((task, index) => (
  <li key={index}>{task.name} - {task.status}</li>
))}
            </ul>
            <h1>Projects</h1>
            <ul>
              {projects.map((project, index) => (
  <li key={index} style={{ listStyle: 'none', margin: '0.5rem 0', padding: 0 }}>
    <button
      style={{
        cursor: 'pointer',
        color: '#fff',
        background: '#007bff',
        border: 'none',
        borderRadius: '4px',
        padding: '0.5rem 1.5rem',
        fontSize: '1rem',
        textDecoration: 'none'
      }}
      onClick={() => setCurrentProject(project)}
    >
      {project.name}
    </button>
  </li>
))}
            </ul>
          </>
        ) : (
          <CreateProject
            onBack={() => setShowCreate(false)}
            onProjectCreated={proj => {
              setProjects([...projects, proj]);
              setShowCreate(false);
              setCurrentProject(proj);
            }}
          />
        )}
      </div>
    </div>
  );
}

ReactDOM.render(<MainPage />, document.getElementById('root'));

// Feature: Creating projects UI
function CreateProject({ onBack, onProjectCreated }) {
  const [project, setProject] = useState({
    name: '',
    teamMembers: [],
    deadline: '',
    tasks: []
  });
  const [currentTeamMember, setCurrentTeamMember] = useState({ name: '', role: '' });
  const [currentTaskName, setCurrentTaskName] = useState('');
  const [currentTaskAssignee, setCurrentTaskAssignee] = useState('');

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
    if (onProjectCreated) onProjectCreated(project);
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', minWidth: 300 }}>
      <label htmlFor="project-name"><strong>Project Name</strong></label>
      <input
        id="project-name"
        type="text"
        value={project.name}
        onChange={(e) => setProject({ ...project, name: e.target.value })}
        required
      />
      {/* Team Members */}
      <div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.5rem' }}>
          <label htmlFor="team-member-name"><strong>Team Member Name</strong></label>
          <input
            id="team-member-name"
            type="text"
            value={currentTeamMember.name}
            onChange={e => setCurrentTeamMember({ ...currentTeamMember, name: e.target.value })}
          />
          <label htmlFor="team-member-role"><strong>Role</strong></label>
          <input
            id="team-member-role"
            type="text"
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
      <label htmlFor="project-deadline"><strong>Project Deadline</strong></label>
      <input
        id="project-deadline"
        type="date"
        value={project.deadline}
        onChange={(e) => setProject({ ...project, deadline: e.target.value })}
      />
      {/* Task creation */}
      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
        <label htmlFor="task-name"><strong>Task Name</strong></label>
        <input
          id="task-name"
          type="text"
          value={currentTaskName}
          onChange={(e) => setCurrentTaskName(e.target.value)}
        />
        <label htmlFor="task-assignee"><strong>Assign to</strong></label>
        <select
          id="task-assignee"
          value={currentTaskAssignee}
          onChange={e => setCurrentTaskAssignee(e.target.value)}
        >
          <option value="">Select team member</option>
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