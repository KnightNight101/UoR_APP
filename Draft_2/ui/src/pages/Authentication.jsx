import React from "react";
import { useNavigate } from "react-router-dom";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Paper from "@mui/material/Paper";
import Stack from "@mui/material/Stack";

function Authentication() {
  const navigate = useNavigate();

  return (
    <Container maxWidth="sm" sx={{ mt: 8 }}>
      <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
        <Box display="flex" flexDirection="column" alignItems="center" gap={3}>
          <Typography variant="h4" gutterBottom>
            Welcome
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
            Please sign in to continue
          </Typography>
          <Stack spacing={2} sx={{ width: "100%" }}>
            <TextField
              label="Username"
              variant="outlined"
              fullWidth
              autoComplete="username"
            />
            <TextField
              label="Password"
              type="password"
              variant="outlined"
              fullWidth
              autoComplete="current-password"
            />
          </Stack>
          <Stack direction="row" spacing={2} sx={{ mt: 3, width: "100%" }} justifyContent="center">
            <Button variant="contained" color="primary" fullWidth>
              Verify
            </Button>
            <Button variant="outlined" color="secondary" fullWidth>
              Reset Password
            </Button>
            <Button
              variant="text"
              color="info"
              fullWidth
              onClick={() => navigate("/dashboard")}
            >
              Debug
            </Button>
          </Stack>
        </Box>
      </Paper>
    </Container>
  );
}

export default Authentication;