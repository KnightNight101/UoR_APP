import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper, IconButton } from '@mui/material';
import { DatePicker, LocalizationProvider } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import RemoveCircleOutlineIcon from '@mui/icons-material/RemoveCircleOutline';

const ProjectCreation = () => {
  const [projectName, setProjectName] = useState('');
  const [projectDeadline, setProjectDeadline] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const handleTaskChange = (index, field, value) => {
    const updatedTasks = [...tasks];
    updatedTasks[index] = { ...updatedTasks[index], [field]: value };
    setTasks(updatedTasks);
  };

  const handleAddTask = () => {
    setTasks([...tasks, { name: '', deadline: null }]);
  };

  const handleRemoveTask = (index) => {
    setTasks(tasks.filter((_, i) => i !== index));
  };

  const handleCreateProject = async () => {
    setCreating(true);
    setError("");
    setSuccess(false);
    const payload = {
      name: projectName,
      deadline: projectDeadline,
      tasks: tasks.map(t => ({
        name: t.name,
        deadline: t.deadline,
      })),
    };
    try {
      const res = await fetch("/api/projects/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      setCreating(false);
      if (res.ok) {
        setSuccess(true);
        setProjectName('');
        setProjectDeadline(null);
        setTasks([]);
        navigate("/dashboard");
      } else {
        setError("Failed to create project");
      }
    } catch (err) {
      setCreating(false);
      setError("Network error");
    }
  };

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: '#f5f5f5',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, minWidth: 350 }}>
          <Typography variant="h5" gutterBottom>
            Create a New Project
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            You will be set as the team leader for this project.
          </Typography>
          <TextField
            label="Project Name"
            variant="outlined"
            fullWidth
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            sx={{ mb: 3 }}
            required
          />
          <DatePicker
            label="Project Deadline (optional)"
            value={projectDeadline}
            onChange={setProjectDeadline}
            slotProps={{ textField: { fullWidth: true, sx: { mb: 3 } } }}
          />
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              Tasks (optional)
            </Typography>
            {tasks.map((task, idx) => (
              <Box key={idx} sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 1 }}>
                <TextField
                  label="Task Name"
                  variant="outlined"
                  value={task.name}
                  onChange={(e) => handleTaskChange(idx, 'name', e.target.value)}
                  sx={{ flex: 2 }}
                  size="small"
                />
                <DatePicker
                  label="Deadline"
                  value={task.deadline}
                  onChange={(date) => handleTaskChange(idx, 'deadline', date)}
                  slotProps={{ textField: { size: 'small', sx: { minWidth: 140 } } }}
                />
                <IconButton
                  aria-label="Remove Task"
                  onClick={() => handleRemoveTask(idx)}
                  color="error"
                  sx={{ ml: 1 }}
                >
                  <RemoveCircleOutlineIcon />
                </IconButton>
              </Box>
            ))}
            <Button
              variant="outlined"
              startIcon={<AddCircleOutlineIcon />}
              onClick={handleAddTask}
              sx={{ mt: 1 }}
            >
              Add Task
            </Button>
          </Box>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            disabled={!projectName || creating}
            onClick={handleCreateProject}
          >
            {creating ? "Creating..." : "Create Project"}
          </Button>
          {error && (
            <Typography color="error" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}
          {success && (
            <Typography color="success.main" sx={{ mt: 2 }}>
              Project created successfully!
            </Typography>
          )}
        </Paper>
      </Box>
    </LocalizationProvider>
  );
};

export default ProjectCreation;