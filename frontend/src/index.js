/* Entry point for React.js application */

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
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '90vh' }}>
      <div style={{ minWidth: 350, background: '#f9f9f9', padding: 32, borderRadius: 12, boxShadow: '0 2px 8px #0001', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <h2>Create New Project</h2>
        <label style={{ width: '100%', marginBottom: 12 }}>
          Project Name:
          <input
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            style={{ width: '100%', marginTop: 4 }}
          />
        </label>
        <label style={{ width: '100%', marginBottom: 12 }}>
          Deadline (optional):
          <input
            type="date"
            value={deadline}
            onChange={e => setDeadline(e.target.value)}
            style={{ width: '100%', marginTop: 4 }}
          />
        </label>
        <h3>Team Members</h3>
        <ul style={{ width: '100%' }}>
          {teamMembers.map((member, idx) => (
            <li key={idx}>
              {member.name} - {member.role}
              <button
                style={{ marginLeft: 8, color: 'red' }}
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
              style={{ width: '100%' }}
            />
          </label>
          <label style={{ flex: 1 }}>
            Role:
            <input
              type="text"
              value={newMember.role}
              onChange={e => setNewMember({ ...newMember, role: e.target.value })}
              style={{ width: '100%' }}
            />
          </label>
          <button type="button" onClick={handleAddTeamMember}>Add</button>
        </div>
        <h3>Tasks</h3>
        <ul style={{ width: '100%' }}>
          {tasks.map((task, idx) => (
            <li key={idx}>
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
            Deadline (optional):
            <input
              type="date"
              value={newTask.deadline}
              onChange={e => setNewTask({ ...newTask, deadline: e.target.value })}
              style={{ width: '100%' }}
            />
          </label>
          <button type="button" onClick={handleAddTask}>Add Task</button>
        </div>
        <div style={{ display: 'flex', gap: 8, width: '100%', marginTop: 16 }}>
          <button
            type="button"
            onClick={() => {
              if (name.trim()) {
                onCreate(name.trim(), deadline, teamMembers, tasks);
              }
            }}
            style={{ flex: 1 }}
          >
            Create
          </button>
          <button type="button" onClick={onCancel} style={{ flex: 1 }}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

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
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'flex-start', minHeight: '90vh' }}>
      {/* Column 1: Team Members */}
      <div style={{ flex: 1, minWidth: 220, background: '#f9f9f9', padding: 24, borderRadius: 12, boxShadow: '0 2px 8px #0001', margin: 8 }}>
        <h3>Team Members</h3>
        <ul style={{ width: '100%' }}>
          {teamMembers.map((member, idx) => (
            <li key={idx}>
              {member.name} - {member.role}
              <button
                style={{ marginLeft: 8, color: 'red' }}
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
      {/* Column 2: Tasks and Subtasks */}
      <div style={{ flex: 2, minWidth: 350, background: '#f9f9f9', padding: 24, borderRadius: 12, boxShadow: '0 2px 8px #0001', margin: 8 }}>
        <div style={{ width: '100%', display: 'flex', gap: 8, justifyContent: 'flex-start', marginBottom: 8 }}>
          <button onClick={onHome}>Back to Home</button>
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
        <div style={{ marginBottom: 16, fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 8 }}>
          Project Deadline: {project.deadline ? project.deadline : <span style={{ color: '#888' }}>No deadline set</span>}
          <input
            type="date"
            value={project.deadline || ''}
            onChange={e => onRename(editName, e.target.value)}
            style={{ marginLeft: 8 }}
          />
        </div>
        <h3>Tasks</h3>
        <ul style={{ width: '100%' }}>
          {tasks.map((task, idx) => (
            <li key={idx} style={{ marginBottom: 16 }}>
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
      <div style={{ flex: 2, minWidth: 350, background: '#f9f9f9', padding: 24, borderRadius: 12, boxShadow: '0 2px 8px #0001', margin: 8 }}>
        <h3>Gantt Chart</h3>
        <GanttChart tasks={tasks} />
      </div>
    </div>
  );
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

  // Helper to get the previous item for dependency lines
  function getPrevItem(i) {
    if (i === 0) return null;
    return allItems[i - 1];
  }

  return (
    <div style={{ overflowX: 'auto', border: '1px solid #ccc', borderRadius: 8, background: '#fff', padding: 8 }}>
      <table style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th style={{ minWidth: 120, textAlign: 'left' }}>Name</th>
            {days.map((d, i) => (
              <th key={i} style={{ minWidth: 40, fontWeight: 'normal', fontSize: 12 }}>
                {d.toISOString().slice(5, 10)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {allItems.map((item, i) => (
            <tr key={i}>
              <td style={{ fontWeight: item.type === 'Task' ? 'bold' : 'normal', paddingLeft: item.type === 'Subtask' ? 24 : 0, position: 'relative' }}>
                {item.name}
                {item.parent && <span style={{ color: '#888', fontSize: 12 }}> (of {item.parent})</span>}
                {item.dependency && getPrevItem(i) && (
                  <span style={{ color: '#2196f3', fontSize: 10, marginLeft: 4 }}>
                    ↳ depends on {getPrevItem(i).name}
                  </span>
                )}
              </td>
              {days.map((d, j) => {
                const isActive = item.start === d.toISOString().slice(0, 10);
                return (
                  <td key={j} style={{
                    background: isActive ? '#4caf50' : undefined,
                    border: '1px solid #eee',
                    height: 18,
                    minWidth: 40
                  }} />
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
}

// ... (RootApp unchanged)

function RootApp() {
  // Example initial state
  const [projects, setProjects] = useState([
    {
      name: "Example Project",
      deadline: "",
      tasks: [],
      teamMembers: []
    }
  ]);
  const [currentProjectIdx, setCurrentProjectIdx] = useState(null);

  // Navigation handlers
  const [creatingProject, setCreatingProject] = useState(false);

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
  const handleRename = newName => {
    setProjects(prev =>
      prev.map((p, i) =>
        i === currentProjectIdx ? { ...p, name: newName } : p
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
    <ProjectDetails
      project={projects[currentProjectIdx]}
      onBack={handleBack}
      onHome={handleHome}
      onRename={handleRename}
      onDelete={handleDelete}
    />
  );
}

ReactDOM.render(<RootApp />, document.getElementById('root'));