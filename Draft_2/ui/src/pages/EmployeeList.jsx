import React, { useState, useEffect } from "react";
import { Grid, Paper, Typography, Checkbox, FormControlLabel, List, ListItem, ListItemText, Select, MenuItem, Button } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import { useNavigate } from "react-router-dom";

const EmployeeList = () => {
  const [users, setUsers] = useState([]);
  const [projectFilter, setProjectFilter] = useState("");
  const [hasOpenTicket, setHasOpenTicket] = useState(false);
  const [projects, setProjects] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch users from backend
    fetch("http://localhost:5000/api/users")
      .then((res) => res.json())
      .then((data) => setUsers(data));

    // TODO: Fetch projects from backend if available
    setProjects(["Project Alpha", "Project Beta", "Project Gamma"]);
  }, []);

  // TODO: Filter logic for hasOpenTicket and projectFilter

  const columns = [
    { field: "id", headerName: "ID", width: 70 },
    { field: "username", headerName: "Username", width: 200 },
    { field: "created_at", headerName: "Onboarding Date", width: 200 },
    // Add more fields as needed
  ];

  return (
    <Grid container spacing={2} sx={{ minHeight: "80vh", maxWidth: "60vw", margin: "0 auto" }}>
      <Grid item xs={3}>
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>
            Filters
          </Typography>
          <FormControlLabel
            control={
              <Checkbox
                checked={hasOpenTicket}
                onChange={(e) => setHasOpenTicket(e.target.checked)}
              />
            }
            label="Has Open Ticket"
          />
          <Typography variant="subtitle1" sx={{ mt: 2 }}>
            Filter by Project
          </Typography>
          <Select
            value={projectFilter}
            onChange={(e) => setProjectFilter(e.target.value)}
            fullWidth
            sx={{ mb: 2 }}
          >
            <MenuItem value="">All Projects</MenuItem>
            {projects.map((proj, idx) => (
              <MenuItem key={idx} value={proj}>
                {proj}
              </MenuItem>
            ))}
          </Select>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 4 }}
            onClick={() => navigate("/add-user")}
          >
            Add User
          </Button>
        </Paper>
      </Grid>
      <Grid item xs={9}>
        <Paper sx={{ p: 2, height: "100%" }}>
          <Typography variant="h6" gutterBottom>
            Employee List
          </Typography>
          <DataGrid
            rows={users}
            columns={columns}
            pageSize={10}
            rowsPerPageOptions={[10]}
            autoHeight
            disableSelectionOnClick
          />
        </Paper>
      </Grid>
    </Grid>
  );
};

export default EmployeeList;