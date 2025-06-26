// Simple React Admin UI for Node Server
const { useState, useEffect } = React;

function App() {
  const [members, setMembers] = useState([]);
  const [projects, setProjects] = useState([]);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch('/members').then(r => r.json()).then(setMembers);
    fetch('/projects').then(r => r.json()).then(setProjects);
    fetch('/logs').then(r => r.json()).then(setLogs);
  }, []);

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'Segoe UI, Arial, sans-serif' }}>
      {/* Column 1: Members */}
      <div style={{ flex: 1, borderRight: '1px solid #ddd', padding: 24, overflowY: 'auto' }}>
        <h2>Members</h2>
        <ul>
          {members.map(m => (
            <li key={m.id || m.name}>{m.name} {m.role ? <span style={{color:'#888'}}>({m.role})</span> : null}</li>
          ))}
        </ul>
      </div>
      {/* Column 2: Projects */}
      <div style={{ flex: 1, borderRight: '1px solid #ddd', padding: 24, overflowY: 'auto' }}>
        <h2>Projects</h2>
        <ul>
          {projects.map(p => (
            <li key={p.id || p.name}>{p.name}</li>
          ))}
        </ul>
      </div>
      {/* Column 3: Event Log */}
      <div style={{ flex: 1, padding: 24, overflowY: 'auto', background: '#f9f9f9' }}>
        <h2>Event Log</h2>
        <ul>
          {logs.map((log, i) => (
            <li key={i} style={{fontSize:14, marginBottom:8}}>
              <span style={{color:'#888'}}>{log.time || ''}</span> {log.message}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

ReactDOM.render(<App />, document.getElementById('root'));