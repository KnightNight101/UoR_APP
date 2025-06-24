import React, { useState } from 'react';

function App() {
  // Initial state for demonstration
  const [tasks, setTasks] = useState([
    { name: 'Initial Task', status: 'Pending', assignee: '', subTasks: [] }
  ]);
  const [teamMembers, setTeamMembers] = useState([
    { name: 'Alice', role: 'Developer' }
  ]);

  // Add Task handler
  const handleAddTask = () => {
    const name = prompt('Enter task name:');
    if (name) {
      // Assign to first team member if present
      const assignee = teamMembers.length > 0 ? teamMembers[0].name : '';
      setTasks(prev => [...prev, { name, status: 'Pending', assignee, subTasks: [] }]);
    }
  };

  // Add Team Member handler
  const handleAddTeamMember = () => {
    const name = prompt('Enter team member name:');
    const role = prompt('Enter team member role:');
    if (name) {
      setTeamMembers(prev => [...prev, { name, role }]);
      // Assign all unassigned tasks to the first member if this is the first member
      setTasks(prev =>
        prev.map(task =>
          !task.assignee ? { ...task, assignee: name } : task
        )
      );
    }
  };

  // Assign/reassign task handler
  const handleAssigneeChange = (idx, newAssignee) => {
    setTasks(prev =>
      prev.map((task, i) =>
        i === idx ? { ...task, assignee: newAssignee } : task
      )
    );
  };

  return (
    <div>
      <h2>Project Page</h2>
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
      <button type="button" onClick={handleAddTask}>Add Task</button>
      <h3>Team Members</h3>
      <ul>
        {teamMembers.map((member, idx) => (
          <li key={idx}>{member.name} - {member.role}</li>
        ))}
      </ul>
      <button type="button" onClick={handleAddTeamMember}>Add Team Member</button>
    </div>
  );
}

export default App;