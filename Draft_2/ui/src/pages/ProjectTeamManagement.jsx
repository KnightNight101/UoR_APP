import React from "react";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

function ProjectTeamManagement() {
  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{ backgroundColor: "background.default", py: { xs: 2, md: 4 } }}
    >
      <Container maxWidth={false} sx={{ maxWidth: "60vw", width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
        <Box display="flex" flexDirection="column" alignItems="center" gap={2} width="100%">
          <Typography variant="h4" gutterBottom>
            Project/Team Management
          </Typography>
          <Typography variant="body1">
            Placeholder for project and team management UI.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}

export default ProjectTeamManagement;