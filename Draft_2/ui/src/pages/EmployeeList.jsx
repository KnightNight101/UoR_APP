import React, { useState } from "react";
import { Grid, Paper, Typography, Checkbox, FormControlLabel, List, ListItem, ListItemText, Select, MenuItem } from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";

// Placeholder projects
const projects = [
  "Project Alpha",
  "Project Beta",
  "Project Gamma"
];

// Placeholder users
const users = [
  {
    id: 1,
    name: "Alice Smith",
    privilege: "Admin",
    onboarding: "2024-01-15",
    hasOpenTicket: true,
    project: "Project Alpha"
  },
  {
    id: 2,
    name: "Bob Johnson",
    privilege: "Member",
    onboarding: "2024-03-22",
    hasOpenTicket: false,
    project: "Project Beta"
  },
  {
    id: 3,
    name: "Carol Lee",
    privilege: "Leader",
    onboarding: "2024-02-10",
    hasOpenTicket: true,
    project: "Project Gamma"
  }
];

const columns = [
  { field: "name", headerName: "Name", flex: 1, sortable: true },
  { field: "privilege", headerName: "Privilege", flex: 1, sortable: true },
  { field: "onboarding", headerName: "Onboarding Date", flex: 1, sortable: true },
  { field: "hasOpenTicket", headerName: "Has Open Ticket", flex: 1, sortable: true, renderCell: (params) => params.value ? "Yes" : "No" },
  { field: "project", headerName: "Project", flex: 1, sortable: true }
];

function EmployeeList() {
  const [filterOpenTicket, setFilterOpenTicket] = useState(false);
  const [filterProject, setFilterProject] = useState("");

  const filteredUsers = users.filter(user => {
    if (filterOpenTicket && !user.hasOpenTicket) return false;
    if (filterProject && user.project !== filterProject) return false;
    return true;
  });

  return (
    <Grid container spacing={2} sx={{ padding: 2 }}>
      {/* Left Column: Filters */}
      <Grid item xs={12} md={4} lg={3}>
        <Paper elevation={3} sx={{ padding: 2, height: "100%" }}>
          <Typography variant="h6" gutterBottom>
            Filter Options
          </Typography>
          <List>
            <ListItem>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={filterOpenTicket}
                    onChange={e => setFilterOpenTicket(e.target.checked)}
                  />
                }
                label="Has open ticket"
              />
            </ListItem>
            <ListItem>
              <Typography variant="subtitle1">Project</Typography>
              <Select
                fullWidth
                value={filterProject}
                onChange={e => setFilterProject(e.target.value)}
                displayEmpty
              >
                <MenuItem value="">All Projects</MenuItem>
                {projects.map(project => (
                  <MenuItem key={project} value={project}>{project}</MenuItem>
                ))}
              </Select>
            </ListItem>
          </List>
        </Paper>
      </Grid>

      {/* Right/Main Column: DataGrid */}
      <Grid item xs={12} md={8} lg={9}>
        <Paper elevation={3} sx={{ padding: 2, height: "100%" }}>
          <Typography variant="h6" gutterBottom>
            Employee List
          </Typography>
          <div style={{ height: 400, width: "100%" }}>
            <DataGrid
              rows={filteredUsers}
              columns={columns}
              pageSize={5}
              rowsPerPageOptions={[5]}
              disableSelectionOnClick
              autoHeight
            />
          </div>
        </Paper>
      </Grid>
    </Grid>
  );
}

export default EmployeeList;