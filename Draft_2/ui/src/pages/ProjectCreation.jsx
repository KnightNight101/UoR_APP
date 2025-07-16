import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper } from '@mui/material';

const ProjectCreation = () => {
  const [projectName, setProjectName] = useState('');

  return (
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
        />
        <Button
          variant="contained"
          color="primary"
          fullWidth
          disabled={!projectName}
        >
          Create Project
        </Button>
      </Paper>
    </Box>
  );
};

export default ProjectCreation;