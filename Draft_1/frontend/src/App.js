import React, { useState } from 'react';

function App() {
  // Authentication state
  const [auth, setAuth] = useState(() => {
    // DEV: Always show login form if ?dev=1 in URL
    if (window.location.search.includes("dev=1")) return "";
    return localStorage.getItem("token") || "";
  });
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
      <div
        style={{
          display: "flex",
          height: "100vh",
          alignItems: "center",
          justifyContent: "center",
          background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)"
        }}
      >
        <form
          onSubmit={handleAuth}
          style={{
            minWidth: 320,
            maxWidth: 400,
            width: "100%",
            padding: "2.5rem 2rem",
            border: "1px solid #e0e0e0",
            borderRadius: 16,
            background: "#fff",
            boxShadow: "0 4px 24px rgba(60, 72, 88, 0.12)",
            display: "flex",
            flexDirection: "column",
            alignItems: "center"
          }}
        >
          <h2 style={{ marginBottom: 20, color: "#2d3748", fontWeight: 700, letterSpacing: 1 }}>Login</h2>
          <div style={{ width: "100%", marginBottom: 18 }}>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={e => setUsername(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 12px",
                marginBottom: 12,
                border: "1px solid #ccc",
                borderRadius: 6,
                fontSize: 16,
                background: "#f9f9fb"
              }}
              autoFocus
            />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              style={{
                width: "100%",
                padding: "10px 12px",
                border: "1px solid #ccc",
                borderRadius: 6,
                fontSize: 16,
                background: "#f9f9fb"
              }}
            />
          </div>
          {error && (
            <div style={{ color: "#e53e3e", marginBottom: 10, width: "100%", textAlign: "center" }}>
              {error}
            </div>
          )}
          <button
            type="submit"
            style={{
              width: "100%",
              padding: "12px 0",
              marginBottom: 10,
              background: "linear-gradient(90deg, #667eea 0%, #5a67d8 100%)",
              color: "#fff",
              border: "none",
              borderRadius: 6,
              fontWeight: 600,
              fontSize: 16,
              cursor: "pointer",
              boxShadow: "0 2px 8px rgba(90,103,216,0.08)"
            }}
          >
            Login
          </button>
          <div style={{ textAlign: "center", color: "#888", marginTop: 8, fontSize: 14 }}>
            Account creation is managed by your administrator.
          </div>
          <div style={{ textAlign: "center", marginTop: 12, width: "100%" }}>
            <button
              type="button"
              style={{
                width: "100%",
                background: "#f1f5f9",
                color: "#333",
                border: "1px solid #bbb",
                borderRadius: 4,
                padding: 10,
                cursor: "pointer",
                fontWeight: 500
              }}
              onClick={devBypass}
            >
              [DEV ONLY] Bypass Login
            </button>
          </div>
        </form>
      </div>
    );
  }

  // Development bypass: skip login for dev/testing
  function devBypass() {
    console.log("[DEV BYPASS] Triggered");
    localStorage.setItem("token", "dev-bypass");
    setAuth("dev-bypass");
    window.location.reload(); // Ensure re-render if state is not updating
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