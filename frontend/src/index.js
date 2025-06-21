// Entry point for React.js application

import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';

ReactDOM.render(<App />, document.getElementById('root'));
// Feature: Creating projects UI

import React, { useState } from 'react';

function CreateProject() {
  const [project, setProject] = useState({
    name: '',
    teamMembers: [],
    deadline: '',
    tasks: []
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch('/create-project', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(project)
    });
    const data = await response.json();
    alert(data.message);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Project Name"
        onChange={(e) => setProject({ ...project, name: e.target.value })}
      />
      {/* Add inputs for team members, deadline, tasks */}
      <button type="submit">Create Project</button>
    </form>
  );
}

export default CreateProject;