import React from "react";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Button from "@mui/material/Button";
import Box from "@mui/material/Box";
import Divider from "@mui/material/Divider";

const placeholderTasks = [
  {
    title: "Task 1",
    subtasks: ["Subtask 1.1", "Subtask 1.2"],
  },
  {
    title: "Task 2",
    subtasks: ["Subtask 2.1"],
  },
];

const placeholderProjects = [
  { name: "Project Alpha", role: "Member" },
  { name: "Project Beta", role: "Owner" },
];

function Dashboard() {
  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Grid container spacing={4}>
        {/* Left Column: To Do List */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              To Do List
            </Typography>
            <List>
              {placeholderTasks.map((task, idx) => (
                <Box key={idx} mb={2}>
                  <ListItem>
                    <ListItemText
                      primary={task.title}
                      primaryTypographyProps={{ fontWeight: "bold" }}
                    />
                  </ListItem>
                  <List component="div" disablePadding sx={{ pl: 3 }}>
                    {task.subtasks.map((sub, subIdx) => (
                      <ListItem key={subIdx}>
                        <ListItemText primary={sub} />
                      </ListItem>
                    ))}
                  </List>
                  {idx < placeholderTasks.length - 1 && <Divider sx={{ mt: 1, mb: 1 }} />}
                </Box>
              ))}
            </List>
          </Paper>
        </Grid>
        {/* Right Column: Projects */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h5">Projects</Typography>
              <Button variant="contained" color="primary">
                Create New Project
              </Button>
            </Box>
            <List>
              {placeholderProjects.map((project, idx) => (
                <ListItem key={idx}>
                  <ListItemText
                    primary={project.name}
                    secondary={`Role: ${project.role}`}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;