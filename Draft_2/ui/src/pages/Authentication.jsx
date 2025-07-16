import React from "react";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

function Authentication() {
  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
        <Typography variant="h4" gutterBottom>
          Authentication Page
        </Typography>
        <Typography variant="body1">
          Placeholder for authentication UI.
        </Typography>
      </Box>
    </Container>
  );
}

export default Authentication;