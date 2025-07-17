import { Routes, Route } from 'react-router-dom';
import Authentication from './pages/Authentication.jsx';
import Dashboard from './pages/Dashboard.jsx';
import ProjectCreation from './pages/ProjectCreation.jsx';
import AdminDashboard from './pages/AdminDashboard.jsx';
import LeaderDashboard from './pages/LeaderDashboard.jsx';
import MemberDashboard from './pages/MemberDashboard.jsx';

import EmployeeList from './pages/EmployeeList.jsx';
import AddUser from './pages/AddUser.jsx';

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
        <Route path="/create-project" element={<ProjectCreation />} />
        <Route path="/admin-dashboard" element={<AdminDashboard />} />
        <Route path="/leader-dashboard" element={<LeaderDashboard />} />
        <Route path="/member-dashboard" element={<MemberDashboard />} />
        <Route path="/employee-list" element={<EmployeeList />} />
        <Route path="/add-user" element={<AddUser />} />
      </Routes>
    </div>
  );
}

export default App;
