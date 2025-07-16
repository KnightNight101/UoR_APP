import React from "react";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

function ProjectTeamManagement() {
  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
        <Typography variant="h4" gutterBottom>
          Project/Team Management
        </Typography>
        <Typography variant="body1">
          Placeholder for project and team management UI.
        </Typography>
      </Box>
    </Container>
  );
}

export default ProjectTeamManagement;