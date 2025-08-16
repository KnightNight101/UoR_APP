import logo from './logo.svg';
import './App.css';

import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [members, setMembers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [logs, setLogs] = useState([]);
  const [users, setUsers] = useState([]);
  const [auth, setAuth] = useState(() => localStorage.getItem("token") || "");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [mode, setMode] = useState("login"); // or "register"
  const [error, setError] = useState("");

  useEffect(() => {
    if (auth) {
      const headers = { Authorization: "Bearer " + auth };
      fetch("/members", { headers }).then(r => r.json()).then(setMembers);
      fetch("/projects", { headers }).then(r => r.json()).then(setProjects);
      fetch("/logs", { headers }).then(r => r.json()).then(setLogs);
      fetch("/users", { headers }).then(r => r.json()).then(setUsers);
    }
  }, [auth]);

  function handleAuth(e) {
    e.preventDefault();
    setError("");
    fetch(`/auth/${mode}`, {
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
          <h2 style={{ marginBottom: 16 }}>{mode === "login" ? "Login" : "Create Account"}</h2>
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
            {mode === "login" ? "Login" : "Register"}
          </button>
          <div style={{ textAlign: "center" }}>
            {mode === "login" ? (
              <span>
                No account?{" "}
                <button type="button" onClick={() => { setMode("register"); setError(""); }} style={{ background: "none", border: "none", color: "#007bff", cursor: "pointer" }}>
                  Register
                </button>
              </span>
            ) : (
              <span>
                Already have an account?{" "}
                <button type="button" onClick={() => { setMode("login"); setError(""); }} style={{ background: "none", border: "none", color: "#007bff", cursor: "pointer" }}>
                  Login
                </button>
              </span>
            )}
          </div>
        </form>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "Segoe UI, Arial, sans-serif" }}>
      {/* Column 1: Members & Registered Users */}
      <div style={{ flex: 1, borderRight: "1px solid #ddd", padding: 24, overflowY: "auto" }}>
        <h2>Members</h2>
        <ul>
          {members.map(m => (
            <li key={m.id || m.name}>
              {m.name} {m.role ? <span style={{ color: "#888" }}>({m.role})</span> : null}
            </li>
          ))}
        </ul>
        <h2 style={{ marginTop: 32 }}>Registered Users</h2>
        <ul>
          {users.map(u => (
            <li key={u.username}>{u.username}</li>
          ))}
        </ul>
      </div>
      {/* Column 2: Projects */}
      <div style={{ flex: 1, borderRight: "1px solid #ddd", padding: 24, overflowY: "auto" }}>
        <h2>Projects</h2>
        <form
          onSubmit={async e => {
            e.preventDefault();
            const name = e.target.elements.projectName.value;
            if (!name) return;
            const headers = { Authorization: "Bearer " + auth, "Content-Type": "application/json" };
            const res = await fetch("/projects", {
              method: "POST",
              headers,
              body: JSON.stringify({ name })
            });
            if (res.ok) {
              const data = await res.json();
              setProjects(projects => [...projects, data]);
              // Navigate to project detail page using returned id
              if (data.id) {
                window.location = `/project/${data.id}`;
              }
            } else {
              alert("Failed to create project");
            }
          }}
          style={{ marginBottom: 16 }}
        >
          <input
            name="projectName"
            type="text"
            placeholder="New project name"
            style={{ marginRight: 8, padding: 6 }}
          />
          <button type="submit" style={{ padding: 6, marginRight: 8 }}>Create Project</button>
          <button
            type="button"
            style={{ padding: 6, background: "#f5f5f5", border: "1px solid #ccc", color: "#333", cursor: "pointer" }}
            onClick={() => { window.location = "/"; }}
          >
            Cancel
          </button>
        </form>
        <ul>
          {projects.map(p => (
            <li
              key={p.id || p.name}
              style={{ cursor: "pointer", color: "#007bff", textDecoration: "underline" }}
              onClick={() => { if (p.id) window.location = `/project/${p.id}`; }}
              tabIndex={0}
              onKeyPress={e => { if (e.key === "Enter" && p.id) window.location = `/project/${p.id}`; }}
              aria-label={`View project ${p.name}`}
            >
              {p.name}
            </li>
          ))}
        </ul>
      </div>
      {/* Column 3: Event Log */}
      <div style={{ flex: 1, padding: 24, overflowY: "auto", background: "#f9f9f9" }}>
        <h2>Event Log</h2>
        <ul>
          {logs.map((log, i) => (
            <li key={i} style={{ fontSize: 14, marginBottom: 8 }}>
              <span style={{ color: "#888" }}>{log.time || ""}</span> {log.message}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default App;