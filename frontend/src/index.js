// DEBUG: index.js loaded
console.log("DEBUG: index.js loaded");
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

// ... (LoginPage and CreateProject unchanged for brevity)

// ProjectDetails: project page with tasks, subtasks, team members, and project deadline
function ProjectDetails({ project, onBack, onHome, onRename, onDelete }) {
  const [tasks, setTasks] = useState(project.tasks);
  const [teamMembers, setTeamMembers] = useState(project.teamMembers);
  const [newTask, setNewTask] = useState({ name: '', status: 'Pending', assignee: '', deadline: '', subTasks: [] });
  const [newMember, setNewMember] = useState({ name: '', role: '' });
  const [editName, setEditName] = useState(project.name);
  const [subTaskInputs, setSubTaskInputs] = useState({}); // { taskIdx: { name: '', status: 'Pending' } }

  const handleAssigneeChange = (idx, newAssignee) => {
    setTasks(prev =>
      prev.map((task, i) =>
        i === idx ? { ...task, assignee: newAssignee } : task
      )
    );
  };

  const handleAddTask = () => {
    if (newTask.name) {
      setTasks(prev => [...prev, { ...newTask, assignee: newTask.assignee || (teamMembers[0]?.name || ''), deadline: newTask.deadline, subTasks: [] }]);
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

  // Subtask handlers
  const handleSubTaskInputChange = (taskIdx, field, value) => {
    setSubTaskInputs(inputs => ({
      ...inputs,
      [taskIdx]: { ...inputs[taskIdx], [field]: value }
    }));
  };

  const handleAddSubTask = (taskIdx) => {
    const input = subTaskInputs[taskIdx] || { name: '', status: 'Pending' };
    if (input.name) {
      setTasks(prev =>
        prev.map((task, i) =>
          i === taskIdx
            ? { ...task, subTasks: [...(task.subTasks || []), { name: input.name, status: input.status || 'Pending' }] }
            : task
        )
      );
      setSubTaskInputs(inputs => ({ ...inputs, [taskIdx]: { name: '', status: 'Pending' } }));
    }
  };

  const handleSubTaskStatusChange = (taskIdx, subIdx, status) => {
    setTasks(prev =>
      prev.map((task, i) =>
        i === taskIdx
          ? {
              ...task,
              subTasks: task.subTasks.map((sub, j) =>
                j === subIdx ? { ...sub, status } : sub
              )
            }
          : task
      )
    );
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
        <div style={{ marginBottom: 16, fontWeight: 'bold' }}>
          Project Deadline: {project.deadline ? project.deadline : <span style={{ color: '#888' }}>No deadline set</span>}
        </div>
        <h3>Tasks</h3>
        <ul style={{ width: '100%' }}>
          {tasks.map((task, idx) => (
            <li key={idx} style={{ marginBottom: 16 }}>
              <div>
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
              </div>
              {/* Subtasks */}
              <div style={{ marginLeft: 24 }}>
                <strong>Subtasks:</strong>
                <ul>
                  {(task.subTasks || []).map((sub, subIdx) => (
                    <li key={subIdx}>
                      {sub.name} - 
                      <select
                        value={sub.status}
                        onChange={e => handleSubTaskStatusChange(idx, subIdx, e.target.value)}
                        style={{ marginLeft: 8 }}
                      >
                        <option value="Pending">Pending</option>
                        <option value="Completed">Completed</option>
                      </select>
                    </li>
                  ))}
                </ul>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <input
                    type="text"
                    placeholder="Subtask Name"
                    value={subTaskInputs[idx]?.name || ''}
                    onChange={e => handleSubTaskInputChange(idx, 'name', e.target.value)}
                  />
                  <select
                    value={subTaskInputs[idx]?.status || 'Pending'}
                    onChange={e => handleSubTaskInputChange(idx, 'status', e.target.value)}
                  >
                    <option value="Pending">Pending</option>
                    <option value="Completed">Completed</option>
                  </select>
                  <button type="button" onClick={() => handleAddSubTask(idx)}>Add Subtask</button>
                </div>
              </div>
            </li>
          ))}
        </ul>
        <div style={{ display: 'flex', gap: 8, width: '100%', marginBottom: 8 }}>
          <label style={{ flex: 1 }}>
            Task Name:
            <input
              type="text"
              value={newTask.name}
              onChange={e => setNewTask({ ...newTask, name: e.target.value })}
              style={{ width: '100%' }}
            />
          </label>
          <label style={{ flex: 1 }}>
            Assignee (optional):
            <input
              type="text"
              value={newTask.assignee}
              onChange={e => setNewTask({ ...newTask, assignee: e.target.value })}
              style={{ width: '100%' }}
            />
          </label>
          <label style={{ flex: 1 }}>
            Task Deadline (optional):
            <input
              type="date"
              value={newTask.deadline}
              onChange={e => setNewTask({ ...newTask, deadline: e.target.value })}
              style={{ width: '100%' }}
            />
          </label>
        </div>
        <button type="button" onClick={handleAddTask} style={{ width: '100%', marginBottom: 24 }}>Add Task</button>
        <h3>Team Members</h3>
        <ul style={{ width: '100%' }}>
          {teamMembers.map((member, idx) => (
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
        <button type="button" onClick={handleAddTeamMember} style={{ width: '100%' }}>Add Team Member</button>
      </div>
    </div>
  );
}

// ... (RootApp unchanged)

ReactDOM.render(<RootApp />, document.getElementById('root'));