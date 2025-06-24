// Entry point for React.js application

import React, { useState } from 'react';
import ReactDOM from 'react-dom';

// MainPage: homepage listing projects and tasks
function MainPage({ projects, onCreateProject, onViewProject, onLogin }) {
  return (
    <div>
      <div style={{ position: 'absolute', top: 0, right: 0 }}>
        <button onClick={onLogin}>Login</button>
        <button>System Settings</button>
        <button>Other Features</button>
      </div>
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
  );
}

// LoginPage: simple login form
function LoginPage({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  return (
    <div>
      <h2>Login</h2>
      <form onSubmit={e => { e.preventDefault(); onLoginSuccess(); }}>
        <input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
        <input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
        <button type="submit">Login</button>
      </form>
    </div>
  );
}

// CreateProject: project creation form
function CreateProject({ onProjectCreated }) {
  const [project, setProject] = useState({
    name: '',
    teamMembers: [],
    deadline: '',
    tasks: []
  });
  const [currentTask, setCurrentTask] = useState({ name: '', status: 'Pending', assignee: '', subTasks: [] });
  const [newMember, setNewMember] = useState({ name: '', role: '' });

  const handleAddTask = () => {
    setProject(prev => ({
      ...prev,
      tasks: [...prev.tasks, { ...currentTask, assignee: currentTask.assignee || (prev.teamMembers[0]?.name || null) }]
    }));
    setCurrentTask({ name: '', status: 'Pending', assignee: '', subTasks: [] });
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
    <form onSubmit={handleSubmit}>
      <h2>Create Project</h2>
      <input type="text" placeholder="Project Name" value={project.name} onChange={e => setProject({ ...project, name: e.target.value })} />
      <input type="date" value={project.deadline} onChange={e => setProject({ ...project, deadline: e.target.value })} />
      <h3>Team Members</h3>
      <ul>
        {project.teamMembers.map((member, idx) => (
          <li key={idx}>{member.name} - {member.role}</li>
        ))}
      </ul>
      <input
        type="text"
        placeholder="Team Member Name"
        value={newMember.name}
        onChange={e => setNewMember({ ...newMember, name: e.target.value })}
      />
      <input
        type="text"
        placeholder="Team Member Role"
        value={newMember.role}
        onChange={e => setNewMember({ ...newMember, role: e.target.value })}
      />
      <button type="button" onClick={handleAddTeamMember}>Add Team Member</button>
      <h3>Tasks</h3>
      <ul>
        {project.tasks.map((task, idx) => (
          <li key={idx}>
            {task.name} - {task.status} - {task.assignee ? task.assignee : 'unassigned'}
          </li>
        ))}
      </ul>
      <input
        type="text"
        placeholder="Task Name"
        value={currentTask.name}
        onChange={e => setCurrentTask({ ...currentTask, name: e.target.value })}
      />
      <input
        type="text"
        placeholder="Assignee (optional)"
        value={currentTask.assignee}
        onChange={e => setCurrentTask({ ...currentTask, assignee: e.target.value })}
      />
      <button type="button" onClick={handleAddTask}>Add Task</button>
      <button type="submit">Create Project</button>
    </form>
  );
}

// ProjectDetails: project page with tasks and team members
function ProjectDetails({ project, onBack, onHome }) {
  const [tasks, setTasks] = useState(project.tasks);
  const [teamMembers, setTeamMembers] = useState(project.teamMembers);
  const [newTask, setNewTask] = useState({ name: '', status: 'Pending', assignee: '', subTasks: [] });
  const [newMember, setNewMember] = useState({ name: '', role: '' });

  const handleAssigneeChange = (idx, newAssignee) => {
    setTasks(prev =>
      prev.map((task, i) =>
        i === idx ? { ...task, assignee: newAssignee } : task
      )
    );
  };

  const handleAddTask = () => {
    if (newTask.name) {
      setTasks(prev => [...prev, { ...newTask, assignee: newTask.assignee || (teamMembers[0]?.name || '') }]);
      setNewTask({ name: '', status: 'Pending', assignee: '', subTasks: [] });
    }
  };

  const handleAddTeamMember = () => {
    if (newMember.name) {
      setTeamMembers(prev => [...prev, { ...newMember }]);
      setNewMember({ name: '', role: '' });
    }
  };

  return (
    <div>
      <button onClick={onBack}>Back to Projects</button>
      <button onClick={onHome}>Home</button>
      <h2>{project.name} - Project Page</h2>
      <h3>Tasks</h3>
      <ul>
        {tasks.map((task, idx) => (
          <li key={idx}>
            {task.name} - {task.status} - 
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
      <input
        type="text"
        placeholder="Task Name"
        value={newTask.name}
        onChange={e => setNewTask({ ...newTask, name: e.target.value })}
      />
      <input
        type="text"
        placeholder="Assignee (optional)"
        value={newTask.assignee}
        onChange={e => setNewTask({ ...newTask, assignee: e.target.value })}
      />
      <button type="button" onClick={handleAddTask}>Add Task</button>
      <h3>Team Members</h3>
      <ul>
        {teamMembers.map((member, idx) => (
          <li key={idx}>{member.name} - {member.role}</li>
        ))}
      </ul>
      <input
        type="text"
        placeholder="Team Member Name"
        value={newMember.name}
        onChange={e => setNewMember({ ...newMember, name: e.target.value })}
      />
      <input
        type="text"
        placeholder="Team Member Role"
        value={newMember.role}
        onChange={e => setNewMember({ ...newMember, role: e.target.value })}
      />
      <button type="button" onClick={handleAddTeamMember}>Add Team Member</button>
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
    setProjects(prev => [...prev, project]);
    setPage('main');
  };
  const handleViewProject = (idx) => {
    setSelectedProjectIdx(idx);
    setPage('details');
  };
  const handleLogin = () => setPage('login');
  const handleLoginSuccess = () => setPage('main');
  const handleBack = () => setPage('main');
  const handleHome = () => setPage('main');

  if (page === 'login') return <LoginPage onLoginSuccess={handleLoginSuccess} />;
  if (page === 'create') return <CreateProject onProjectCreated={handleProjectCreated} />;
  if (page === 'details' && selectedProjectIdx !== null)
    return <ProjectDetails project={projects[selectedProjectIdx]} onBack={handleBack} onHome={handleHome} />;
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