import React, { useState, useEffect } from "react";
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Grid,
  MenuItem,
  IconButton,
  InputAdornment,
} from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";

const permissions = ["Admin", "Employee"];

function AddUser() {
  const [form, setForm] = useState({
    firstName: "",
    middleName: "",
    lastName: "",
    jobRole: "",
    permissions: "",
  });

  const [userCount, setUserCount] = useState(null);

  useEffect(() => {
    // Fetch user count from backend
    fetch("/api/user-count")
      .then((res) => res.json())
      .then((data) => setUserCount(data.count))
      .catch(() => setUserCount(0));
  }, []);

  // Generate initials
  const initials =
    (form.firstName[0] || "") +
    (form.middleName[0] || "") +
    (form.lastName[0] || "");

  // Username: initials + (userCount + 1)
  const username =
    initials +
    (userCount !== null ? userCount + 1 : "");

  const password = "changeme123";

  const [copied, setCopied] = useState({ username: false, password: false });

  const handleCopy = (type, value) => {
    navigator.clipboard.writeText(value);
    setCopied((prev) => ({ ...prev, [type]: true }));
    setTimeout(() => setCopied((prev) => ({ ...prev, [type]: false })), 1200);
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Placeholder: handle form submission
  };

  return (
    <Container maxWidth="sm" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h5" gutterBottom>
          Add New User
        </Typography>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={2} direction="column">
            <Grid item xs={12}>
              <TextField
                label="First Name"
                name="firstName"
                value={form.firstName}
                onChange={handleChange}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Middle Name"
                name="middleName"
                value={form.middleName}
                onChange={handleChange}
                fullWidth
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Last Name"
                name="lastName"
                value={form.lastName}
                onChange={handleChange}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Job Role"
                name="jobRole"
                value={form.jobRole}
                onChange={handleChange}
                fullWidth
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                select
                label="Permissions"
                name="permissions"
                value={form.permissions}
                onChange={handleChange}
                fullWidth
                required
              >
                {permissions.map((perm) => (
                  <MenuItem key={perm} value={perm}>
                    {perm}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Username"
                value={username}
                InputProps={{
                  readOnly: true,
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => handleCopy("username", username)}
                        edge="end"
                        size="small"
                        aria-label="copy username"
                      >
                        <ContentCopyIcon fontSize="small" />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                fullWidth
              />
              {copied.username && (
                <Typography variant="caption" color="success.main">
                  Copied!
                </Typography>
              )}
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Default Password"
                value={password}
                InputProps={{
                  readOnly: true,
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => handleCopy("password", password)}
                        edge="end"
                        size="small"
                        aria-label="copy password"
                      >
                        <ContentCopyIcon fontSize="small" />
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                fullWidth
              />
              {copied.password && (
                <Typography variant="caption" color="success.main">
                  Copied!
                </Typography>
              )}
            </Grid>
            <Grid item xs={12}>
              <Button type="submit" variant="contained" color="primary" fullWidth>
                Submit
              </Button>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </Container>
  );
}

export default AddUser;