// Entry point for React.js application

import React, { useState } from 'react';
import ReactDOM from 'react-dom';

// MainPage: homepage listing projects and today's to-do list
function MainPage({ projects, onCreateProject, onViewProject, onLogin }) {
  const allTasks = projects.flatMap(project =>
    project.tasks.map(task => ({
      ...task,
      projectName: project.name
    }))
  );

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '90vh' }}>
      <div style={{ width: '90%', maxWidth: 1000, background: '#f9f9f9', padding: 32, borderRadius: 12, boxShadow: '0 2px 8px #0001' }}>
        <div style={{ position: 'absolute', top: 0, right: 0 }}>
          <button onClick={onLogin}>Login</button>
          <button>System Settings</button>
          <button>Other Features</button>
        </div>
        <div style={{ display: 'flex', gap: '2em', alignItems: 'flex-start' }}>
          {/* Projects column */}
          <div style={{ flex: 1 }}>
            <h1>Projects</h1>
            <ul>
              {projects.map((project, idx) => (
                <li key={idx}>
                  <button onClick={() => onViewProject(idx)}>{project.name}</button>
                </li>
              ))}
            </ul>
            <button onClick={onCreateProject}>Create New Project</button>
          </div>
          {/* Today's To Do List column */}
          <div style={{ flex: 1 }}>
            <h1>Today's To Do List</h1>
            <ul>
              {allTasks.length === 0 && <li>No tasks for today.</li>}
              {allTasks.map((task, idx) => (
                <li key={idx}>
                  {task.name} ({task.status}) {task.deadline ? `[Due: ${task.deadline}]` : ''} <span style={{ color: '#888' }}>in {task.projectName}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

// LoginPage: simple login form
function LoginPage({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '90vh' }}>
      <form
        onSubmit={e => { e.preventDefault(); onLoginSuccess(); }}
        style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: 350, background: '#f9f9f9', padding: 32, borderRadius: 12, boxShadow: '0 2px 8px #0001' }}
      >
        <h2>Login</h2>
        <label style={{ width: '100%', marginBottom: 8 }}>
          Email:
          <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} style={{ width: '100%' }} />
        </label>
        <label style={{ width: '100%', marginBottom: 8 }}>
          Password:
          <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} style={{ width: '100%' }} />
        </label>
        <button type="submit" style={{ width: '100%' }}>Login</button>
      </form>
    </div>
  );
}

// CreateProject: project creation form
function CreateProject({ onProjectCreated, onCancel }) {
  const [project, setProject] = useState({
    name: '',
    teamMembers: [],
    deadline: '',
    tasks: []
  });
  const [currentTask, setCurrentTask] = useState({ name: '', status: 'Pending', assignee: '', deadline: '', subTasks: [] });
  const [newMember, setNewMember] = useState({ name: '', role: '' });

  const handleAddTask = () => {
    setProject(prev => ({
      ...prev,
      tasks: [...prev.tasks, { ...currentTask, assignee: currentTask.assignee || (prev.teamMembers[0]?.name || null) }]
    }));
    setCurrentTask({ name: '', status: 'Pending', assignee: '', deadline: '', subTasks: [] });
  };

  const handleAddTeamMember = () => {
    if (newMember.name) {
      setProject(prev => {
        const updatedMembers = [...prev.teamMembers, { ...newMember }];
        if (updatedMembers.length === 1) {
          setCurrentTask(ct => ({ ...ct, assignee: newMember.name }));
        }
        return { ...prev, teamMembers: updatedMembers };
      });
      setNewMember({ name: '', role: '' });
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onProjectCreated(project);
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '90vh' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: 350, background: '#f9f9f9', padding: 32, borderRadius: 12, boxShadow: '0 2px 8px #0001' }}>
        <h2>Create Project</h2>
        <label style={{ width: '100%', marginBottom: 8 }}>
          Project Name:
          <input type="text" value={project.name} onChange={e => setProject({ ...project, name: e.target.value })} style={{ width: '100%' }} />
        </label>
        <label style={{ width: '100%', marginBottom: 8 }}>
          Project Deadline:
          <input type="date" value={project.deadline} onChange={e => setProject({ ...project, deadline: e.target.value })} style={{ width: '100%' }} />
        </label>
        <h3>Team Members</h3>
        <ul style={{ width: '100%' }}>
          {project.teamMembers.map((member, idx) => (
            <li key={idx}>{member.name} - {member.role}</li>
          ))}
        </ul>
        <div style={{ display: 'flex', gap: 8, width: '100%', marginBottom: 8 }}>
          <label style={{ flex: 1 }}>
            Team Member Name:
            <input
              type="text"
              value={newMember.name}
              onChange={e => setNewMember({ ...newMember, name: e.target.value })}
              style={{ width: '100%' }}
            />
          </label>
          <label style={{ flex: 1 }}>
            Team Member Role:
            <input
              type="text"
              value={newMember.role}
              onChange={e => setNewMember({ ...newMember, role: e.target.value })}
              style={{ width: '100%' }}
            />
          </label>
        </div>
        <button type="button" onClick={handleAddTeamMember} style={{ width: '100%', marginBottom: 16 }}>Add Team Member</button>
        <h3>Tasks</h3>
        <ul style={{ width: '100%' }}>
          {project.tasks.map((task, idx) => (
            <li key={idx}>
              {task.name} - {task.status} - {task.assignee ? task.assignee : 'unassigned'} {task.deadline ? `[Due: ${task.deadline}]` : ''}
            </li>
          ))}
        </ul>
        <div style={{ display: 'flex', gap: 8, width: '100%', marginBottom: 8 }}>
          <label style={{ flex: 1 }}>
            Task Name:
            <input
              type="text"
              value={currentTask.name}
              onChange={e => setCurrentTask({ ...currentTask, name: e.target.value })}
              style={{ width: '100%' }}
            />
          </label>
          <label style={{ flex: 1 }}>
            Assignee (optional):
            <input
              type="text"
              value={currentTask.assignee}
              onChange={e => setCurrentTask({ ...currentTask, assignee: e.target.value })}
              style={{ width: '100%' }}
            />
          </label>
          <label style={{ flex: 1 }}>
            Task Deadline (optional):
            <input
              type="date"
              value={currentTask.deadline}
              onChange={e => setCurrentTask({ ...currentTask, deadline: e.target.value })}
              style={{ width: '100%' }}
            />
          </label>
        </div>
        <button type="button" onClick={handleAddTask} style={{ width: '100%', marginBottom: 24 }}>Add Task</button>
        <div style={{ display: 'flex', gap: 16, width: '100%', justifyContent: 'center', marginTop: 16 }}>
          <button type="submit">Create Project</button>
          <button type="button" onClick={onCancel}>Cancel</button>
        </div>
      </form>
    </div>
  );
}

// ProjectDetails: project page with tasks and team members
function ProjectDetails({ project, onBack, onHome, onRename, onDelete }) {
  const [tasks, setTasks] = useState(project.tasks);
  const [teamMembers, setTeamMembers] = useState(project.teamMembers);
  const [newTask, setNewTask] = useState({ name: '', status: 'Pending', assignee: '', deadline: '', subTasks: [] });
  const [newMember, setNewMember] = useState({ name: '', role: '' });
  const [editName, setEditName] = useState(project.name);

  const handleAssigneeChange = (idx, newAssignee) => {
    setTasks(prev =>
      prev.map((task, i) =>
        i === idx ? { ...task, assignee: newAssignee } : task
      )
    );
  };

  const handleAddTask = () => {
    if (newTask.name) {
      setTasks(prev => [...prev, { ...newTask, assignee: newTask.assignee || (teamMembers[0]?.name || ''), deadline: newTask.deadline }]);
      setNewTask({ name: '', status: 'Pending', assignee: '', deadline: '', subTasks: [] });
    }
  };

  const handleAddTeamMember = () => {
    if (newMember.name) {
      setTeamMembers(prev => [...prev, { ...newMember }]);
      setNewMember({ name: '', role: '' });
    }
  };

  const handleRename = () => {
    if (editName.trim()) {
      onRename(editName.trim());
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '90vh' }}>
      <div style={{ minWidth: 350, background: '#f9f9f9', padding: 32, borderRadius: 12, boxShadow: '0 2px 8px #0001', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ width: '100%', display: 'flex', gap: 8, justifyContent: 'flex-start', marginBottom: 8 }}>
          <button onClick={onBack}>Back to Projects</button>
          <button onClick={onHome}>Home</button>
          <button onClick={onDelete} style={{marginLeft: '1em', color: 'red'}}>Delete Project</button>
        </div>
        <h2>
          <input
            type="text"
            value={editName}
            onChange={e => setEditName(e.target.value)}
            style={{ fontSize: '1.2em', fontWeight: 'bold' }}
          />
          <button type="button" onClick={handleRename}>Rename</button>
        </h2>
        <h3>Tasks</h3>
        <ul style={{ width: '100%' }}>
          {tasks.map((task, idx) => (
            <li key={idx}>
              {task.name} - {task.status} - 
              {task.assignee ? task.assignee : 'unassigned'}
              {task.deadline ? ` [Due: ${task.deadline}]` : ''}
              <select
                value={task.assignee || ''}
                onChange={e => handleAssigneeChange(idx, e.target.value)}
              >
                <option value="">unassigned</option>
                {teamMembers.map((member, i) => (
                  <option key={i} value={member.name}>{member.name}</option>
                ))}
              </select>
            </li>
          ))}
        </ul>
        <label style={{ width: '100%', marginBottom: 8 }}>
          Task Name:
          <input
            type="text"
            value={newTask.name}
            onChange={e => setNewTask({ ...newTask, name: e.target.value })}
            style={{ width: '100%' }}
          />
        </label>
        <label style={{ width: '100%', marginBottom: 8 }}>
          Assignee (optional):
          <input
            type="text"
            value={newTask.assignee}
            onChange={e => setNewTask({ ...newTask, assignee: e.target.value })}
            style={{ width: '100%' }}
          />
        </label>
        <label style={{ width: '100%', marginBottom: 8 }}>
          Task Deadline (optional):
          <input
            type="date"
            value={newTask.deadline}
            onChange={e => setNewTask({ ...newTask, deadline: e.target.value })}
            style={{ width: '100%' }}
          />
        </label>
        <button type="button" onClick={handleAddTask} style={{ width: '100%', marginBottom: 24 }}>Add Task</button>
        <h3>Team Members</h3>
        <ul style={{ width: '100%' }}>
          {teamMembers.map((member, idx) => (
            <li key={idx}>{member.name} - {member.role}</li>
          ))}
        </ul>
        <label style={{ width: '100%', marginBottom: 8 }}>
          Team Member Name:
          <input
            type="text"
            value={newMember.name}
            onChange={e => setNewMember({ ...newMember, name: e.target.value })}
            style={{ width: '100%' }}
          />
        </label>
        <label style={{ width: '100%', marginBottom: 8 }}>
          Team Member Role:
          <input
            type="text"
            value={newMember.role}
            onChange={e => setNewMember({ ...newMember, role: e.target.value })}
            style={{ width: '100%' }}
          />
        </label>
        <button type="button" onClick={handleAddTeamMember} style={{ width: '100%' }}>Add Team Member</button>
      </div>
    </div>
  );
}

// Root app logic with simple navigation
function RootApp() {
  const [page, setPage] = useState('main');
  const [projects, setProjects] = useState([]);
  const [selectedProjectIdx, setSelectedProjectIdx] = useState(null);

  const handleCreateProject = () => setPage('create');
  const handleProjectCreated = (project) => {
    setProjects(prev => {
      const newProjects = [...prev, project];
      setSelectedProjectIdx(newProjects.length - 1);
      setPage('details');
      return newProjects;
    });
  };
  const handleViewProject = (idx) => {
    setSelectedProjectIdx(idx);
    setPage('details');
  };
  const handleLogin = () => setPage('login');
  const handleLoginSuccess = () => setPage('main');
  const handleBack = () => setPage('main');
  const handleHome = () => setPage('main');
  const handleRename = (newName) => {
    setProjects(prev =>
      prev.map((proj, idx) =>
        idx === selectedProjectIdx ? { ...proj, name: newName } : proj
      )
    );
  };
  const handleCancelCreate = () => setPage('main');
  const handleDeleteProject = () => {
    setProjects(prev => prev.filter((_, idx) => idx !== selectedProjectIdx));
    setPage('main');
  };

  if (page === 'login') return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  if (page === 'create') return <CreateProject onProjectCreated={handleProjectCreated} onCancel={handleCancelCreate} />;
  if (page === 'details' && selectedProjectIdx !== null)
    return (
      <ProjectDetails
        project={projects[selectedProjectIdx]}
        onBack={handleBack}
        onHome={handleHome}
        onRename={handleRename}
        onDelete={handleDeleteProject}
      />
    );
  return (
    <MainPage
      projects={projects}
      onCreateProject={handleCreateProject}
      onViewProject={handleViewProject}
      onLogin={handleLogin}
    />
  );
}

ReactDOM.render(<RootApp />, document.getElementById('root'));