import React from "react";
import Header from "../components/Header.jsx";
import { Grid, Paper, Typography, List, ListItem, Button, ListItemText } from "@mui/material";

import { useNavigate } from "react-router-dom";

function AdminDashboard() {
  const navigate = useNavigate();
  return (
    <>
      <Header />
      <Grid container spacing={2} sx={{ padding: 2 }}>
        {/* Left Column: To-do Lists */}
        <Grid item xs={12} md={3}>
          <Paper elevation={3} sx={{ padding: 2, height: "100%" }}>
            <Typography variant="h6" gutterBottom>
              To-do Lists
            </Typography>
            <List>
              <ListItem>
                <ListItemText primary="Task 1: Placeholder" secondary="Subtask A, Subtask B" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Task 2: Placeholder" secondary="Subtask C" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Task 3: Placeholder" />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      
        {/* Center Column: Projects */}
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ padding: 2, height: "100%" }}>
            <Typography variant="h6" gutterBottom>
              Projects
            </Typography>
            <List>
              <ListItem>
                <ListItemText primary="Project Alpha" secondary="Status: In Progress" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Project Beta" secondary="Status: Completed" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Project Gamma" secondary="Status: Pending" />
              </ListItem>
            </List>
          </Paper>
        </Grid>
      
        {/* Right Column: Menu */}
        <Grid item xs={12} md={3}>
          <Paper elevation={3} sx={{ padding: 2, height: "100%" }}>
            <Typography variant="h6" gutterBottom>
              Menu
            </Typography>
            <List>
              <ListItem>
                <Button fullWidth variant="contained" color="primary">
                  Tickets
                </Button>
              </ListItem>
              <ListItem>
                <Button fullWidth variant="contained" color="secondary">
                  Event Log
                </Button>
              </ListItem>
              <ListItem>
                <Button
                  fullWidth
                  variant="contained"
                  color="success"
                  onClick={() => navigate("/employee-list")}
                >
                  Employee Lists
                </Button>
              </ListItem>
            </List>
          </Paper>
        </Grid>
      </Grid>
    </>
  );
}

export default AdminDashboard;