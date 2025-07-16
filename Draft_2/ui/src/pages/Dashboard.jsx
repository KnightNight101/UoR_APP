import React from "react";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

function Dashboard() {
  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1">
          Placeholder for dashboard UI.
        </Typography>
      </Box>
    </Container>
  );
}

export default Dashboard;