import { Routes, Route } from 'react-router-dom';
import Authentication from './pages/Authentication.jsx';
import Dashboard from './pages/Dashboard.jsx';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Authentication />} />
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  );
}

export default App;
