/* Entry point for React.js application */

import React, { useState } from 'react';
import ReactDOM from 'react-dom';

// Minimalist Modern Theme
const theme = {
  background: "#f6f7fb",
  card: "#fff",
  border: "#e0e3ea",
  accent: "#4f8cff",
  accentLight: "#eaf1ff",
  text: "#222",
  textLight: "#888",
  shadow: "0 2px 16px 0 rgba(80, 120, 200, 0.06)",
  radius: "12px"
};

function ThemedContainer({ children, style = {}, ...props }) {
  return (
    <div
      style={{
        background: theme.background,
        minHeight: "100vh",
        color: theme.text,
        fontFamily: "Inter, Segoe UI, Arial, sans-serif",
        fontSize: 16,
        ...style
      }}
      {...props}
    >
      {children}
    </div>
  );
}

// MainPage: homepage listing projects and today's to-do list
function MainPage({ projects, onCreateProject, onViewProject, onLogin }) {
  console.log("MainPage render", projects);
  const allTasks = projects.flatMap(project =>
    project.tasks.map(task => ({
      ...task,
      projectName: project.name
    }))
  );

  return (
    <ThemedContainer>
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '90vh'
        }}
      >
        <div
          style={{
            width: '90%',
            maxWidth: 1100,
            background: theme.card,
            padding: 32,
            borderRadius: theme.radius,
            boxShadow: theme.shadow,
            border: `1px solid ${theme.border}`,
            position: 'relative'
          }}
        >
          <div style={{ position: 'absolute', top: 24, right: 32, display: 'flex', gap: 12 }}>
            <button style={{
              background: theme.accent,
              color: "#fff",
              border: "none",
              borderRadius: theme.radius,
              padding: "8px 18px",
              fontWeight: 500,
              cursor: "pointer",
              boxShadow: theme.shadow
            }} onClick={onLogin}>Login</button>
            <button style={{
              background: theme.accentLight,
              color: theme.accent,
              border: "none",
              borderRadius: theme.radius,
              padding: "8px 18px",
              fontWeight: 500,
              cursor: "pointer"
            }}>System Settings</button>
            <button style={{
              background: theme.accentLight,
              color: theme.accent,
              border: "none",
              borderRadius: theme.radius,
              padding: "8px 18px",
              fontWeight: 500,
              cursor: "pointer"
            }}>Other Features</button>
          </div>
          <div style={{ display: 'flex', gap: '2em', alignItems: 'flex-start' }}>
            {/* Projects column */}
            <div style={{ flex: 1 }}>
              <h1 style={{ fontWeight: 700, fontSize: 28, marginBottom: 16, color: theme.text }}>Projects</h1>
              <ul style={{ padding: 0, listStyle: "none" }}>
                {projects.map((project, idx) => (
                  <li key={idx} style={{ marginBottom: 10 }}>
                    <button
                      onClick={() => onViewProject(idx)}
                      style={{
                        background: theme.accentLight,
                        color: theme.accent,
                        border: "none",
                        borderRadius: theme.radius,
                        padding: "10px 18px",
                        fontWeight: 500,
                        cursor: "pointer",
                        width: "100%",
                        textAlign: "left",
                        boxShadow: theme.shadow
                      }}
                    >
                      {project.name}
                    </button>
                  </li>
                ))}
              </ul>
              <button
                onClick={onCreateProject}
                style={{
                  background: theme.accent,
                  color: "#fff",
                  border: "none",
                  borderRadius: theme.radius,
                  padding: "10px 18px",
                  fontWeight: 600,
                  cursor: "pointer",
                  marginTop: 12,
                  width: "100%",
                  boxShadow: theme.shadow
                }}
              >
                + Create New Project
              </button>
            </div>
            {/* Today's To Do List column */}
            <div style={{ flex: 1 }}>
              <h1 style={{ fontWeight: 700, fontSize: 28, marginBottom: 16, color: theme.text }}>Today's To Do List</h1>
              <ul style={{ padding: 0, listStyle: "none" }}>
                {allTasks.length === 0 && <li style={{ color: theme.textLight }}>No tasks for today.</li>}
                {allTasks.map((task, idx) => (
                  <li key={idx} style={{ marginBottom: 10 }}>
                    <span style={{
                      background: theme.accentLight,
                      color: theme.accent,
                      borderRadius: theme.radius,
                      padding: "6px 12px",
                      fontWeight: 500,
                      marginRight: 8
                    }}>
                      {task.name}
                    </span>
                    <span style={{ color: theme.textLight }}>
                      ({task.status}) {task.deadline ? `[Due: ${task.deadline}]` : ''} in {task.projectName}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </ThemedContainer>
  );
}

function CreateProject({ onCreate, onCancel }) {
  const [name, setName] = useState('');
  const [deadline, setDeadline] = useState('');
  const [teamMembers, setTeamMembers] = useState([]);
  const [newMember, setNewMember] = useState({ name: '', role: '' });
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState({ name: '', status: 'Pending', assignee: '', deadline: '', subTasks: [] });

  const handleAddTeamMember = () => {
    if (newMember.name) {
      setTeamMembers(prev => [...prev, { ...newMember }]);
      setNewMember({ name: '', role: '' });
    }
  };

  const handleAddTask = () => {
    if (newTask.name) {
      setTasks(prev => [...prev, { ...newTask, assignee: newTask.assignee || (teamMembers[0]?.name || ''), deadline: newTask.deadline, subTasks: [] }]);
      setNewTask({ name: '', status: 'Pending', assignee: '', deadline: '', subTasks: [] });
    }
  };

  return (
    <ThemedContainer>
      <div
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '90vh'
        }}
      >
        <div
          style={{
            width: '90%',
            maxWidth: 600,
            background: theme.card,
            padding: 32,
            borderRadius: theme.radius,
            boxShadow: theme.shadow,
            border: `1px solid ${theme.border}`,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center'
          }}
        >
          <h2 style={{ fontWeight: 700, fontSize: 24, marginBottom: 16, color: theme.text }}>Create New Project</h2>
          <label style={{ width: '100%', marginBottom: 12 }}>
            Project Name:
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              style={{
                width: '100%',
                marginTop: 4,
                border: `1px solid ${theme.border}`,
                borderRadius: theme.radius,
                padding: "8px",
                fontSize: 16
              }}
            />
          </label>
          <label style={{ width: '100%', marginBottom: 12 }}>
            Deadline (optional):
            <input
              type="date"
              value={deadline}
              onChange={e => setDeadline(e.target.value)}
              style={{
                width: '100%',
                marginTop: 4,
                border: `1px solid ${theme.border}`,
                borderRadius: theme.radius,
                padding: "8px",
                fontSize: 16
              }}
            />
          </label>
          <h3 style={{ color: theme.accent, fontWeight: 600, marginTop: 16 }}>Team Members</h3>
          <ul style={{ width: '100%', padding: 0, listStyle: "none" }}>
            {teamMembers.map((member, idx) => (
              <li key={idx} style={{ marginBottom: 8 }}>
                {member.name} - {member.role}
                <button
                  style={{
                    marginLeft: 8,
                    color: "#fff",
                    background: theme.accent,
                    border: "none",
                    borderRadius: theme.radius,
                    padding: "4px 10px",
                    cursor: "pointer"
                  }}
                  onClick={() => {
                    setTeamMembers(prev => prev.filter((_, i) => i !== idx));
                  }}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
          <div style={{ display: 'flex', gap: 8, width: '100%', marginBottom: 8 }}>
            <label style={{ flex: 1 }}>
              Name:
              <input
                type="text"
                value={newMember.name}
                onChange={e => setNewMember({ ...newMember, name: e.target.value })}
                style={{
                  width: '100%',
                  border: `1px solid ${theme.border}`,
                  borderRadius: theme.radius,
                  padding: "6px",
                  fontSize: 15
                }}
              />
            </label>
            <label style={{ flex: 1 }}>
              Role:
              <input
                type="text"
                value={newMember.role}
                onChange={e => setNewMember({ ...newMember, role: e.target.value })}
                style={{
                  width: '100%',
                  border: `1px solid ${theme.border}`,
                  borderRadius: theme.radius,
                  padding: "6px",
                  fontSize: 15
                }}
              />
            </label>
            <button
              type="button"
              onClick={handleAddTeamMember}
              style={{
                background: theme.accent,
                color: "#fff",
                border: "none",
                borderRadius: theme.radius,
                padding: "8px 14px",
                fontWeight: 500,
                cursor: "pointer"
              }}
            >
              Add
            </button>
          </div>
          <h3 style={{ color: theme.text, fontWeight: 600, marginTop: 16 }}>Tasks</h3>
          <ul style={{ width: '100%', padding: 0, listStyle: "none" }}>
            {tasks.map((task, idx) => (
              <li key={idx} style={{ marginBottom: 8 }}>
                {task.name} - {task.status} - {task.assignee || 'unassigned'}
                {task.deadline ? ` [Due: ${task.deadline}]` : ''}
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
                style={{
                  width: '100%',
                  border: `1px solid ${theme.border}`,
                  borderRadius: theme.radius,
                  padding: "6px",
                  fontSize: 15
                }}
              />
            </label>
            <label style={{ flex: 1 }}>
              Assignee (optional):
              <select
                value={newTask.assignee}
                onChange={e => setNewTask({ ...newTask, assignee: e.target.value })}
                style={{
                  width: '100%',
                  border: `1px solid ${theme.border}`,
                  borderRadius: theme.radius,
                  padding: "6px",
                  fontSize: 15
                }}
              >
                <option value="">unassigned</option>
                {teamMembers.map((member, idx) => (
                  <option key={idx} value={member.name}>{member.name}</option>
                ))}
              </select>
            </label>
            <label style={{ flex: 1 }}>
              Deadline (optional):
              <input
                type="date"
                value={newTask.deadline}
                onChange={e => setNewTask({ ...newTask, deadline: e.target.value })}
                style={{
                  width: '100%',
                  border: `1px solid ${theme.border}`,
                  borderRadius: theme.radius,
                  padding: "6px",
                  fontSize: 15
                }}
              />
            </label>
            <button
              type="button"
              onClick={handleAddTask}
              style={{
                background: theme.accent,
                color: "#fff",
                border: "none",
                borderRadius: theme.radius,
                padding: "8px 14px",
                fontWeight: 500,
                cursor: "pointer"
              }}
            >
              Add Task
            </button>
          </div>
          <div style={{ display: 'flex', gap: 8, width: '100%', marginTop: 16 }}>
            <button
              type="button"
              onClick={() => {
                if (name.trim()) {
                  onCreate(name.trim(), deadline, teamMembers, tasks);
                }
              }}
              style={{
                flex: 1,
                background: theme.accent,
                color: "#fff",
                border: "none",
                borderRadius: theme.radius,
                padding: "10px 18px",
                fontWeight: 600,
                cursor: "pointer",
                boxShadow: theme.shadow
              }}
            >
              Create
            </button>
            <button
              type="button"
              onClick={onCancel}
              style={{
                flex: 1,
                background: theme.accentLight,
                color: theme.accent,
                border: "none",
                borderRadius: theme.radius,
                padding: "10px 18px",
                fontWeight: 600,
                cursor: "pointer",
                boxShadow: theme.shadow
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </ThemedContainer>
  );
}

// ProjectDetails: project page with tasks, subtasks, team members, and project deadline
function ProjectDetails({ project, onBack, onHome, onRename, onDelete, onOpenGantt }) {
  console.log("ProjectDetails render", project);
  const [tasks, setTasks] = useState(project.tasks);
  const [teamMembers, setTeamMembers] = useState(project.teamMembers);
  const [newTask, setNewTask] = useState({ name: '', status: 'Pending', assignee: '', deadline: '', subTasks: [] });
  const [newMember, setNewMember] = useState({ name: '', role: '' });
  const [editName, setEditName] = useState(project.name);
  const [subTaskInputs, setSubTaskInputs] = useState({}); // { taskIdx: { name: '', status: 'Pending' } }
  const [draggedTaskIdx, setDraggedTaskIdx] = useState(null);
  const [draggedSubTask, setDraggedSubTask] = useState({ parentIdx: null, subIdx: null });
  const [dragOverTaskIdx, setDragOverTaskIdx] = useState(null);
  const [dragOverSubTask, setDragOverSubTask] = useState({ parentIdx: null, subIdx: null });

  const handleAssigneeChange = (idx, newAssignee) => {
    setTasks(prev =>
      prev.map((task, i) =>
        i === idx ? { ...task, assignee: newAssignee } : task
      )
    );
  };

  const handleAddTask = () => {
    if (newTask.name) {
      const now = new Date().toISOString().slice(0, 10);
      setTasks(prev => [
        ...prev,
        {
          ...newTask,
          assignee: newTask.assignee || (teamMembers[0]?.name || ''),
          start: newTask.start || now,
          deadline: newTask.deadline,
          subTasks: []
        }
      ]);
      setNewTask({ name: '', status: 'Pending', assignee: '', deadline: '', start: '', subTasks: [] });
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
      onRename(editName.trim(), project.deadline);
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
      const now = new Date().toISOString().slice(0, 10);
      setTasks(prev =>
        prev.map((task, i) =>
          i === taskIdx
            ? {
                ...task,
                subTasks: [
                  ...(task.subTasks || []),
                  {
                    name: input.name,
                    status: input.status || 'Pending',
                    assignee: input.assignee || '',
                    start: input.start || now,
                    deadline: input.deadline || ''
                  }
                ]
              }
            : task
        )
      );
      setSubTaskInputs(inputs => ({ ...inputs, [taskIdx]: { name: '', status: 'Pending', assignee: '', deadline: '', start: '' } }));
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
    <ThemedContainer>
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-start', minHeight: '90vh' }}>
        {/* Column 1: Team Members */}
        <div style={{
          flex: 1,
          minWidth: 220,
          background: theme.card,
          padding: 24,
          borderRadius: theme.radius,
          boxShadow: theme.shadow,
          border: `1px solid ${theme.border}`,
          margin: 8
        }}>
          <h3 style={{ color: theme.accent, fontWeight: 700, marginBottom: 16 }}>Team Members</h3>
          <ul style={{ width: '100%', padding: 0, listStyle: "none" }}>
            {teamMembers.map((member, idx) => (
              <li key={idx} style={{ marginBottom: 8 }}>
                {member.name} - {member.role}
                <button
                  style={{
                    marginLeft: 8,
                    color: "#fff",
                    background: theme.accent,
                    border: "none",
                    borderRadius: theme.radius,
                    padding: "4px 10px",
                    cursor: "pointer"
                  }}
                  onClick={() => {
                    setTeamMembers(prev => prev.filter((_, i) => i !== idx));
                    setTasks(prev =>
                      prev.map(task => ({
                        ...task,
                        assignee: task.assignee === member.name ? '' : task.assignee,
                        subTasks: (task.subTasks || []).map(sub =>
                          sub.assignee === member.name ? { ...sub, assignee: '' } : sub
                        ),
                      }))
                    );
                  }}
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
          <div style={{ display: 'flex', gap: 8, width: '100%', marginBottom: 8 }}>
            <label style={{ flex: 1 }}>
              Team Member Name:
              <input
                type="text"
                value={newMember.name}
                onChange={e => setNewMember({ ...newMember, name: e.target.value })}
                style={{
                  width: '100%',
                  border: `1px solid ${theme.border}`,
                  borderRadius: theme.radius,
                  padding: "6px",
                  fontSize: 15
                }}
              />
            </label>
            <label style={{ flex: 1 }}>
              Team Member Role:
              <input
                type="text"
                value={newMember.role}
                onChange={e => setNewMember({ ...newMember, role: e.target.value })}
                style={{
                  width: '100%',
                  border: `1px solid ${theme.border}`,
                  borderRadius: theme.radius,
                  padding: "6px",
                  fontSize: 15
                }}
              />
            </label>
          </div>
          <button
            type="button"
            onClick={handleAddTeamMember}
            style={{
              background: theme.accent,
              color: "#fff",
              border: "none",
              borderRadius: theme.radius,
              padding: "8px 14px",
              fontWeight: 500,
              cursor: "pointer",
              width: "100%"
            }}
          >
            Add Team Member
          </button>
        </div>
        {/* Column 2: Tasks and Subtasks */}
        <div style={{
          flex: 2,
          minWidth: 350,
          background: theme.card,
          padding: 24,
          borderRadius: theme.radius,
          boxShadow: theme.shadow,
          border: `1px solid ${theme.border}`,
          margin: 8
        }}>
          <div style={{ width: '100%', display: 'flex', gap: 8, justifyContent: 'flex-start', marginBottom: 8 }}>
            <button
              onClick={onHome}
              style={{
                background: theme.accentLight,
                color: theme.accent,
                border: "none",
                borderRadius: theme.radius,
                padding: "8px 18px",
                fontWeight: 500,
                cursor: "pointer"
              }}
            >Back to Home</button>
            <button
              onClick={onDelete}
              style={{
                marginLeft: '1em',
                color: "#fff",
                background: "#ff4f4f",
                border: "none",
                borderRadius: theme.radius,
                padding: "8px 18px",
                fontWeight: 500,
                cursor: "pointer"
              }}
            >Delete Project</button>
          </div>
          <h2 style={{ color: theme.accent, fontWeight: 700, marginBottom: 16 }}>
            <input
              type="text"
              value={editName}
              onChange={e => setEditName(e.target.value)}
              style={{
                fontSize: '1.2em',
                fontWeight: 'bold',
                border: `1px solid ${theme.border}`,
                borderRadius: theme.radius,
                padding: "6px 12px",
                color: theme.text,
                background: theme.card,
                marginRight: 8
              }}
            />
            <button
              type="button"
              onClick={handleRename}
              style={{
                background: theme.accent,
                color: "#fff",
                border: "none",
                borderRadius: theme.radius,
                padding: "6px 16px",
                fontWeight: 500,
                cursor: "pointer"
              }}
            >Rename</button>
          </h2>
          <div style={{ marginBottom: 16, fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 8 }}>
            Project Deadline: {project.deadline ? project.deadline : <span style={{ color: theme.textLight }}>No deadline set</span>}
            <input
              type="date"
              value={project.deadline || ''}
              onChange={e => onRename(editName, e.target.value)}
              style={{
                marginLeft: 8,
                border: `1px solid ${theme.border}`,
                borderRadius: theme.radius,
                padding: "6px 12px",
                fontSize: 15
              }}
            />
          </div>
          <h3 style={{ color: theme.text, fontWeight: 600, marginTop: 16 }}>Tasks</h3>
          <ul style={{ width: '100%', padding: 0, listStyle: "none" }}>
          {tasks.map((task, idx) => (
            <li
              key={idx}
              style={{
                marginBottom: 16,
                background: dragOverTaskIdx === idx ? '#e0f7fa' : undefined,
                opacity: draggedTaskIdx === idx ? 0.5 : 1,
                cursor: 'move'
              }}
              draggable
              onDragStart={() => setDraggedTaskIdx(idx)}
              onDragOver={e => {
                e.preventDefault();
                setDragOverTaskIdx(idx);
              }}
              onDrop={e => {
                e.preventDefault();
                if (draggedTaskIdx !== null && draggedTaskIdx !== idx) {
                  setTasks(prev => {
                    const updated = [...prev];
                    const [moved] = updated.splice(draggedTaskIdx, 1);
                    updated.splice(idx, 0, moved);
                    return updated;
                  });
                }
                setDraggedTaskIdx(null);
                setDragOverTaskIdx(null);
              }}
              onDragEnd={() => {
                setDraggedTaskIdx(null);
                setDragOverTaskIdx(null);
              }}
            >
              <div>
                {task.name} - {task.status}
                <input
                  type="date"
                  value={task.start || ''}
                  onChange={e => {
                    const newStart = e.target.value;
                    setTasks(prev =>
                      prev.map((t, i) =>
                        i === idx ? { ...t, start: newStart } : t
                      )
                    );
                  }}
                  style={{ marginLeft: 8 }}
                  placeholder="Start"
                />
                <input
                  type="date"
                  value={task.deadline || ''}
                  onChange={e => {
                    const newDeadline = e.target.value;
                    setTasks(prev =>
                      prev.map((t, i) =>
                        i === idx ? { ...t, deadline: newDeadline } : t
                      )
                    );
                  }}
                  style={{ marginLeft: 8 }}
                  placeholder="Deadline"
                />
                <select
                  value={task.assignee || ''}
                  onChange={e => handleAssigneeChange(idx, e.target.value)}
                  style={{ marginLeft: 8 }}
                >
                  <option value="">unassigned</option>
                  {teamMembers.map((member, i) => (
                    <option key={i} value={member.name}>{member.name}</option>
                  ))}
                </select>
                {idx > 0 && (
                  <label style={{ marginLeft: 8 }}>
                    <input
                      type="checkbox"
                      checked={!!task.dependency}
                      onChange={e => {
                        const checked = e.target.checked;
                        setTasks(prev =>
                          prev.map((t, i) =>
                            i === idx ? { ...t, dependency: checked } : t
                          )
                        );
                      }}
                    />
                    Dependent on previous
                  </label>
                )}
                <button
                  style={{ marginLeft: 8, color: 'red' }}
                  onClick={() => {
                    setTasks(prev => prev.filter((_, i) => i !== idx));
                  }}
                >
                  Remove Task
                </button>
              </div>
              {/* Subtasks */}
              <div style={{ marginLeft: 24 }}>
                <strong>Subtasks:</strong>
                <ul>
                  {(task.subTasks || []).map((sub, subIdx) => (
                    <li
                      key={subIdx}
                      style={{
                        background:
                          dragOverSubTask.parentIdx === idx && dragOverSubTask.subIdx === subIdx
                            ? '#e0f7fa'
                            : undefined,
                        opacity:
                          draggedSubTask.parentIdx === idx && draggedSubTask.subIdx === subIdx
                            ? 0.5
                            : 1,
                        cursor: 'move'
                      }}
                      draggable
                      onDragStart={() => setDraggedSubTask({ parentIdx: idx, subIdx })}
                      onDragOver={e => {
                        e.preventDefault();
                        setDragOverSubTask({ parentIdx: idx, subIdx });
                      }}
                      onDrop={e => {
                        e.preventDefault();
                        if (
                          draggedSubTask.parentIdx === idx &&
                          draggedSubTask.subIdx !== null &&
                          draggedSubTask.subIdx !== subIdx
                        ) {
                          setTasks(prev => {
                            const updated = [...prev];
                            const subTasks = [...updated[idx].subTasks];
                            const [moved] = subTasks.splice(draggedSubTask.subIdx, 1);
                            subTasks.splice(subIdx, 0, moved);
                            updated[idx] = { ...updated[idx], subTasks };
                            return updated;
                          });
                        }
                        setDraggedSubTask({ parentIdx: null, subIdx: null });
                        setDragOverSubTask({ parentIdx: null, subIdx: null });
                      }}
                      onDragEnd={() => {
                        setDraggedSubTask({ parentIdx: null, subIdx: null });
                        setDragOverSubTask({ parentIdx: null, subIdx: null });
                      }}
                    >
                      {sub.name} -
                      <select
                        value={sub.status}
                        onChange={e => handleSubTaskStatusChange(idx, subIdx, e.target.value)}
                        style={{ marginLeft: 8 }}
                      >
                        <option value="Pending">Pending</option>
                        <option value="Completed">Completed</option>
                      </select>
                      <input
                        type="date"
                        value={sub.start || ''}
                        onChange={e => {
                          const newStart = e.target.value;
                          setTasks(prev =>
                            prev.map((task, tIdx) =>
                              tIdx === idx
                                ? {
                                    ...task,
                                    subTasks: task.subTasks.map((s, sIdx) =>
                                      sIdx === subIdx ? { ...s, start: newStart } : s
                                    )
                                  }
                                : task
                            )
                          );
                        }}
                        style={{ marginLeft: 8 }}
                        placeholder="Start"
                      />
                      <input
                        type="date"
                        value={sub.deadline || ''}
                        onChange={e => {
                          const newDeadline = e.target.value;
                          setTasks(prev =>
                            prev.map((task, tIdx) =>
                              tIdx === idx
                                ? {
                                    ...task,
                                    subTasks: task.subTasks.map((s, sIdx) =>
                                      sIdx === subIdx ? { ...s, deadline: newDeadline } : s
                                    )
                                  }
                                : task
                            )
                          );
                        }}
                        style={{ marginLeft: 8 }}
                        placeholder="Deadline"
                      />
                      <select
                        value={sub.assignee || ''}
                        onChange={e => {
                          const newAssignee = e.target.value;
                          setTasks(prev =>
                            prev.map((task, tIdx) =>
                              tIdx === idx
                                ? {
                                    ...task,
                                    subTasks: task.subTasks.map((s, sIdx) =>
                                      sIdx === subIdx ? { ...s, assignee: newAssignee } : s
                                    )
                                  }
                                : task
                            )
                          );
                        }}
                        style={{ marginLeft: 8 }}
                      >
                        <option value="">unassigned</option>
                        {teamMembers.map((member, i) => (
                          <option key={i} value={member.name}>{member.name}</option>
                        ))}
                      </select>
                      {subIdx > 0 && (
                        <label style={{ marginLeft: 8 }}>
                          <input
                            type="checkbox"
                            checked={!!sub.dependency}
                            onChange={e => {
                              const checked = e.target.checked;
                              setTasks(prev =>
                                prev.map((task, tIdx) =>
                                  tIdx === idx
                                    ? {
                                        ...task,
                                        subTasks: task.subTasks.map((s, sIdx) =>
                                          sIdx === subIdx ? { ...s, dependency: checked } : s
                                        )
                                      }
                                    : task
                                )
                              );
                            }}
                          />
                          Dependent on previous
                        </label>
                      )}
                      <button
                        style={{ marginLeft: 8, color: 'red' }}
                        onClick={() => {
                          setTasks(prev =>
                            prev.map((task, tIdx) =>
                              tIdx === idx
                                ? {
                                    ...task,
                                    subTasks: task.subTasks.filter((_, sIdx) => sIdx !== subIdx)
                                  }
                                : task
                            )
                          );
                        }}
                      >
                        Remove Subtask
                      </button>
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
                  <input
                    type="date"
                    value={subTaskInputs[idx]?.start || ''}
                    onChange={e => handleSubTaskInputChange(idx, 'start', e.target.value)}
                    placeholder="Start"
                  />
                  <input
                    type="date"
                    value={subTaskInputs[idx]?.deadline || ''}
                    onChange={e => handleSubTaskInputChange(idx, 'deadline', e.target.value)}
                    placeholder="Deadline"
                  />
                  <select
                    value={subTaskInputs[idx]?.assignee || ''}
                    onChange={e => handleSubTaskInputChange(idx, 'assignee', e.target.value)}
                  >
                    <option value="">unassigned</option>
                    {teamMembers.map((member, i) => (
                      <option key={i} value={member.name}>{member.name}</option>
                    ))}
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
              <select
                value={newTask.assignee}
                onChange={e => setNewTask({ ...newTask, assignee: e.target.value })}
                style={{ width: '100%' }}
              >
                <option value="">unassigned</option>
                {teamMembers.map((member, idx) => (
                  <option key={idx} value={member.name}>{member.name}</option>
                ))}
              </select>
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
        </div>
        {/* Column 3: Gantt Chart */}
        <div style={{ flex: 2, minWidth: 350, background: '#f9f9f9', padding: 24, borderRadius: 12, boxShadow: '0 2px 8px #0001', margin: 8, cursor: 'pointer' }} onClick={onOpenGantt}>
          <h3>Gantt Chart</h3>
          <GanttChart tasks={tasks} />
          <div style={{ color: theme.textLight, fontSize: 14, marginTop: 8, textAlign: 'center' }}>
            Click to expand
          </div>
        </div>
      </div>
    </ThemedContainer>
  );
}
  // --- GanttChart Component ---
  function GanttChart({ tasks }) {
  // Flatten tasks and subtasks into a single array with type and parent info
  const allItems = [];
  tasks.forEach((task, idx) => {
    if (task.deadline) {
      allItems.push({
        name: task.name,
        start: task.start || task.deadline,
        end: task.deadline,
        type: 'Task',
        parent: null,
        dependency: !!task.dependency,
        index: idx,
      });
    }
    (task.subTasks || []).forEach((sub, subIdx) => {
      if (sub.deadline) {
        allItems.push({
          name: sub.name,
          start: sub.start || sub.deadline,
          end: sub.deadline,
          type: 'Subtask',
          parent: task.name,
          dependency: !!sub.dependency,
          index: idx + subIdx / 100, // for ordering
        });
      }
    });
  });

  // Find min/max dates for chart range
  const allDates = allItems.map(i => i.start).filter(Boolean);
  const minDate = allDates.length ? new Date(Math.min(...allDates.map(d => new Date(d)))) : new Date();
  const maxDate = allDates.length ? new Date(Math.max(...allDates.map(d => new Date(d)))) : new Date();

  // Generate columns for each date in range
  const days = [];
  for (let d = new Date(minDate); d <= maxDate; d.setDate(d.getDate() + 1)) {
    days.push(new Date(d));
  }

  return (
    <div style={{ width: '100%', border: '1px solid #ccc', borderRadius: 8, background: '#fff', padding: 8, display: 'flex', flexDirection: 'row' }}>
      {/* Left: Text info (40%) */}
      <div style={{ flex: '0 0 40%', maxWidth: '40%' }}>
        <table style={{ borderCollapse: 'collapse', width: '100%' }}>
          <thead>
            <tr>
              <th style={{ minWidth: 120, textAlign: 'left' }}>Name</th>
              <th style={{ minWidth: 90 }}>Start</th>
              <th style={{ minWidth: 90 }}>End</th>
              <th style={{ minWidth: 90 }}>Duration</th>
              <th style={{ minWidth: 120 }}>Dependencies</th>
            </tr>
          </thead>
          <tbody>
            {allItems.map((item, i) => {
              const startDate = item.start ? new Date(item.start) : null;
              const endDate = item.end ? new Date(item.end) : null;
              let duration = '';
              if (startDate && endDate) {
                duration = Math.max(1, Math.round((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1) + ' day(s)';
              }
              let dependencyText = '';
              // Dependency logic placeholder
              return (
                <tr key={i}>
                  <td style={{ fontWeight: item.type === 'Task' ? 'bold' : 'normal', paddingLeft: item.type === 'Subtask' ? 24 : 0, position: 'relative' }}>
                    {item.name}
                    {item.parent && <span style={{ color: '#888', fontSize: 12 }}> (of {item.parent})</span>}
                  </td>
                  <td>{item.start || ''}</td>
                  <td>{item.end || ''}</td>
                  <td>{duration}</td>
                  <td>{dependencyText}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      {/* Right: Bar chart (60%) */}
      <div style={{ flex: '0 0 60%', maxWidth: '60%', paddingLeft: 16, overflow: 'hidden' }}>
        {/* Dates row */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${days.length}, 1fr)`,
            marginBottom: 4,
            width: '100%',
          }}
        >
          {days.map((d, i) => (
            <div
              key={i}
              style={{
                textAlign: 'center',
                fontSize: 12,
                fontWeight: 'normal',
                color: '#333',
                borderRight: i === days.length - 1 ? 'none' : '1px solid #eee',
                overflow: 'hidden',
                whiteSpace: 'nowrap',
                textOverflow: 'ellipsis',
              }}
            >
              {d.toISOString().slice(5, 10)}
            </div>
          ))}
        </div>
        {/* Bars */}
        <div style={{ width: '100%' }}>
          {allItems.map((item, i) => {
            const startDate = item.start ? new Date(item.start) : null;
            const endDate = item.end ? new Date(item.end) : null;
            let startIdx = -1;
            let endIdx = -1;
            if (startDate && endDate) {
              startIdx = days.findIndex(d => d.toISOString().slice(0, 10) === item.start);
              endIdx = days.findIndex(d => d.toISOString().slice(0, 10) === item.end);
            }
            return (
              <div
                key={i}
                style={{
                  display: 'grid',
                  gridTemplateColumns: `repeat(${days.length}, 1fr)`,
                  alignItems: 'center',
                  height: 22,
                  width: '100%',
                  background: 'transparent'
                }}
              >
                {Array.from({ length: days.length }).map((_, j) => {
                  const isBar =
                    startIdx >= 0 &&
                    endIdx >= startIdx &&
                    j >= startIdx &&
                    j <= endIdx;
                  return (
                    <div
                      key={j}
                      style={{
                        height: 14,
                        borderRadius: 4,
                        background: isBar ? '#4caf50' : 'transparent',
                        margin: isBar ? '0 1px' : undefined,
                        transition: 'background 0.2s',
                        width: '100%',
                        gridColumn: j + 1,
                        zIndex: isBar ? 1 : 0,
                      }}
                    />
                  );
                })}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// --- Full Gantt Chart Page ---
function FullGanttPage({ project, onClose }) {
  const { tasks, teamMembers, name } = project;
  return (
    <ThemedContainer>
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        width: '100vw',
        alignItems: 'center',
        justifyContent: 'flex-start',
        padding: 0
      }}>
        <div style={{
          width: '100%',
          display: 'flex',
          flexDirection: 'row',
          flex: 1,
          alignItems: 'stretch',
          marginTop: 32
        }}>
          {/* Left: Tasks/Subtasks */}
          <div style={{
            minWidth: 300,
            background: theme.card,
            borderRight: `1px solid ${theme.border}`,
            padding: 24,
            boxShadow: theme.shadow,
            borderRadius: `${theme.radius} 0 0 ${theme.radius}`,
            overflowY: 'auto'
          }}>
            <h2 style={{ color: theme.accent, fontWeight: 700, marginBottom: 16 }}>{name} - Tasks</h2>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {tasks.map((task, idx) => (
                <li key={idx} style={{ marginBottom: 12 }}>
                  <strong>{task.name}</strong>
                  <ul style={{ listStyle: 'circle', marginLeft: 24 }}>
                    {(task.subTasks || []).map((sub, subIdx) => (
                      <li key={subIdx}>{sub.name}</li>
                    ))}
                  </ul>
                </li>
              ))}
            </ul>
          </div>
          {/* Center: Gantt Chart */}
          <div style={{
            flex: 1,
            background: '#fff',
            padding: 32,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <div style={{ width: '100%', maxWidth: 1200 }}>
              <GanttChart tasks={tasks} />
            </div>
          </div>
        </div>
        {/* Bottom: Team Members */}
        <div style={{
          width: '100%',
          background: theme.accentLight,
          padding: '16px 0',
          borderTop: `1px solid ${theme.border}`,
          display: 'flex',
          justifyContent: 'center',
          gap: 32
        }}>
          {teamMembers.map((member, idx) => (
            <div key={idx} style={{
              background: theme.card,
              borderRadius: theme.radius,
              boxShadow: theme.shadow,
              padding: '8px 24px',
              margin: '0 8px',
              minWidth: 120,
              textAlign: 'center'
            }}>
              <div style={{ fontWeight: 600 }}>{member.name}</div>
              <div style={{ color: theme.textLight }}>{member.role}</div>
            </div>
          ))}
        </div>
        <button
          onClick={onClose}
          style={{
            position: 'fixed',
            top: 24,
            right: 32,
            background: theme.accent,
            color: '#fff',
            border: 'none',
            borderRadius: theme.radius,
            padding: '10px 24px',
            fontWeight: 600,
            fontSize: 16,
            cursor: 'pointer',
            boxShadow: theme.shadow,
            zIndex: 100
          }}
        >
          Close
        </button>
      </div>
    </ThemedContainer>
  );
}
// --- Root App and Render ---
function RootApp() {
  // Debug: log state on each render
  console.log("RootApp loaded");
  // Example initial state
  const [projects, setProjects] = React.useState([
    {
      name: "Example Project",
      deadline: "",
      tasks: [],
      teamMembers: []
    }
  ]);
  const [currentProjectIdx, setCurrentProjectIdx] = React.useState(null);
  const [fullGanttProject, setFullGanttProject] = React.useState(null);

  // Navigation handlers
  const [creatingProject, setCreatingProject] = React.useState(false);

  const handleCreateProject = () => {
    setCreatingProject(true);
  };

  const handleProjectCreated = (name, deadline) => {
    setProjects(prev => [...prev, { name, deadline: deadline || "", tasks: [], teamMembers: [] }]);
    setCreatingProject(false);
  };

  const handleCancelCreate = () => {
    setCreatingProject(false);
  };
  const handleViewProject = idx => setCurrentProjectIdx(idx);
  const handleBack = () => setCurrentProjectIdx(null);
  const handleHome = () => setCurrentProjectIdx(null);
  const handleRename = (newName, newDeadline) => {
    setProjects(prev =>
      prev.map((p, i) =>
        i === currentProjectIdx
          ? {
              ...p,
              name: newName !== undefined ? newName : p.name,
              deadline: newDeadline !== undefined ? newDeadline : p.deadline
            }
          : p
      )
    );
  };
  const handleDelete = () => {
    if (window.confirm("Delete this project?")) {
      setProjects(prev => prev.filter((_, i) => i !== currentProjectIdx));
      setCurrentProjectIdx(null);
    }
  };
  const handleLogin = () => alert("Login not implemented.");

  if (creatingProject) {
    return (
      <CreateProject
        onCreate={handleProjectCreated}
        onCancel={handleCancelCreate}
      />
    );
  }

  if (currentProjectIdx === null) {
    return (
      <MainPage
        projects={projects}
        onCreateProject={handleCreateProject}
        onViewProject={handleViewProject}
        onLogin={handleLogin}
      />
    );
  }
  return (
    fullGanttProject !== null ? (
      <FullGanttPage
        project={projects[fullGanttProject]}
        onClose={() => setFullGanttProject(null)}
      />
    ) : (
      <ProjectDetails
        project={projects[currentProjectIdx]}
        onBack={handleBack}
        onHome={handleHome}
        onRename={handleRename}
        onDelete={handleDelete}
        onOpenGantt={() => setFullGanttProject(currentProjectIdx)}
      />
    )
  );
}

import App from "./App";
ReactDOM.render(<App />, document.getElementById('root'))