import { Routes, Route } from 'react-router-dom';
import Authentication from './pages/Authentication.jsx';
import Dashboard from './pages/Dashboard.jsx';

function App() {
  return (
    <div
      style={{
        maxWidth: '60vw',
        width: '100%',
        margin: '0 auto',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: 'transparent',
      }}
    >
      <Routes>
        <Route path="/" element={<Authentication />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </div>
  );
}

export default App;
