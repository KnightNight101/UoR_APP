import React from "react";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

function FileManagement() {
  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{ backgroundColor: "background.default", py: { xs: 2, md: 4 } }}
    >
      <Container maxWidth="sm" sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <Box display="flex" flexDirection="column" alignItems="center" gap={2} width="100%">
          <Typography variant="h4" gutterBottom>
            File Management
          </Typography>
          <Typography variant="body1">
            Placeholder for file management UI.
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}

export default FileManagement;