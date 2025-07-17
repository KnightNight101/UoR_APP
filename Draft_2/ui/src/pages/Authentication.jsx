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
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{ backgroundColor: "background.default", py: { xs: 2, md: 4 } }}
    >
      <Container maxWidth={false} sx={{ maxWidth: "60vw", width: "100%", display: "flex", flexDirection: "column", alignItems: "center" }}>
        <Paper elevation={3} sx={{ p: { xs: 2, sm: 4 }, borderRadius: 3, width: "100%" }}>
          <Box display="flex" flexDirection="column" alignItems="center" gap={3} width="100%">
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
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mt: 3, width: "100%" }} justifyContent="center">
              <Button variant="contained" color="primary" fullWidth>
                Verify
              </Button>
              <Button variant="outlined" color="secondary" fullWidth>
                Reset Password
              </Button>
            </Stack>
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2} sx={{ mt: 2, width: "100%" }} justifyContent="center">
              <Button
                variant="contained"
                color="info"
                fullWidth
                onClick={() => navigate("/admin-dashboard")}
              >
                IT/Admin
              </Button>
              <Button
                variant="contained"
                color="success"
                fullWidth
                onClick={() => navigate("/leader-dashboard")}
              >
                Team Leader
              </Button>
              <Button
                variant="contained"
                color="warning"
                fullWidth
                onClick={() => navigate("/member-dashboard")}
              >
                Team Member
              </Button>
            </Stack>
          </Box>
        </Paper>
      </Container>
    </Box>
  );
}

export default Authentication;