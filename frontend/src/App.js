import React, { useState } from 'react';

function App() {
  // Authentication state
  const [auth, setAuth] = useState(() => localStorage.getItem("token") || "");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mode] = useState("login"); // Registration disabled
  const [error, setError] = useState("");

  // App state
  const [tasks, setTasks] = useState([
    { name: 'Initial Task', status: 'Pending', assignee: '', subTasks: [] }
  ]);
  const [teamMembers, setTeamMembers] = useState([
    { name: 'Alice', role: 'Developer' }
  ]);

  // Auth handlers
  function handleAuth(e) {
    e.preventDefault();
    setError("");
    fetch(`http://localhost:4000/auth/${mode}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    })
      .then(async r => {
        if (!r.ok) {
          const data = await r.json();
          throw new Error(data.error || "Auth failed");
        }
        return r.json();
      })
      .then(data => {
        if (data.token) {
          localStorage.setItem("token", data.token);
          setAuth(data.token);
        } else {
          setMode("login");
          setError("Registration successful. Please log in.");
        }
      })
      .catch(err => setError(err.message));
  }

  if (!auth) {
    return (
      <div style={{ display: "flex", height: "100vh", alignItems: "center", justifyContent: "center" }}>
        <form onSubmit={handleAuth} style={{ minWidth: 320, padding: 32, border: "1px solid #ddd", borderRadius: 8, background: "#fff" }}>
          <h2 style={{ marginBottom: 16 }}>Login</h2>
          <div style={{ marginBottom: 12 }}>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              style={{ width: "100%", padding: 8, marginBottom: 8 }}
              autoFocus
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              style={{ width: "100%", padding: 8 }}
            />
          </div>
          {error && <div style={{ color: "red", marginBottom: 8 }}>{error}</div>}
          <button type="submit" style={{ width: "100%", padding: 10, marginBottom: 8 }}>
            Login
          </button>
          <div style={{ textAlign: "center", color: "#888", marginTop: 8 }}>
            Account creation is managed by your administrator.
          </div>
          <button
            type="button"
            style={{ width: "100%", marginTop: 16, background: "#eee", color: "#333", border: "1px solid #bbb", borderRadius: 4, padding: 8, cursor: "pointer" }}
            onClick={devBypass}
          >
            [DEV ONLY] Bypass Login
          </button>
        </form>
      </div>
    );
  }

  // Development bypass: skip login for dev/testing
  function devBypass() {
    localStorage.setItem("token", "dev-bypass");
    setAuth("dev-bypass");
  }

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
    // Add a dev bypass button for development only
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