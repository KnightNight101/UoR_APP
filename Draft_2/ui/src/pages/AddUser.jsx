import React, { useState } from "react";
import { Box, Button, TextField, Typography, MenuItem, Select, InputLabel, FormControl, Alert } from "@mui/material";
import ContentCopyIcon from "@mui/icons-material/ContentCopy";
import { useNavigate } from "react-router-dom";

const DEFAULT_PASSWORD = "changeme123";

const AddUser = () => {
  const [firstName, setFirstName] = useState("");
  const [middleName, setMiddleName] = useState("");
  const [lastName, setLastName] = useState("");
  const [jobRole, setJobRole] = useState("");
  const [permission, setPermission] = useState("Employee");
  const [employeeCount, setEmployeeCount] = useState(0);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  React.useEffect(() => {
    fetch("http://localhost:5000/api/user-count")
      .then((res) => res.json())
      .then((data) => setEmployeeCount(data.count || 0));
  }, []);

  const initials = `${firstName.charAt(0)}${middleName.charAt(0)}${lastName.charAt(0)}`.toLowerCase();
  const username = `${initials}${employeeCount + 1}`;
  const password = DEFAULT_PASSWORD;

  const handleCopy = (text) => {
    navigator.clipboard.writeText(text);
  };

  const handleSubmit = async () => {
    setError("");
    setSuccess("");
    try {
      const res = await fetch("http://localhost:5000/api/users", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          password,
          role: permission === "Admin" ? "admin" : "user",
          firstName,
          middleName,
          lastName,
          jobRole,
          onboarding: new Date().toISOString(),
        }),
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess("User added successfully!");
        setTimeout(() => navigate("/employee-list"), 1500);
      } else {
        setError(data.error || data.message || JSON.stringify(data));
      }
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Box sx={{ maxWidth: "60vw", margin: "0 auto", p: 4 }}>
      <Typography variant="h5" gutterBottom>
        Onboard New Employee
      </Typography>
      <TextField
        label="First Name"
        value={firstName}
        onChange={(e) => setFirstName(e.target.value)}
        fullWidth
        sx={{ mb: 2 }}
      />
      <TextField
        label="Middle Name"
        value={middleName}
        onChange={(e) => setMiddleName(e.target.value)}
        fullWidth
        sx={{ mb: 2 }}
      />
      <TextField
        label="Last Name"
        value={lastName}
        onChange={(e) => setLastName(e.target.value)}
        fullWidth
        sx={{ mb: 2 }}
      />
      <TextField
        label="Job Role"
        value={jobRole}
        onChange={(e) => setJobRole(e.target.value)}
        fullWidth
        sx={{ mb: 2 }}
      />
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Permissions</InputLabel>
        <Select
          value={permission}
          label="Permissions"
          onChange={(e) => setPermission(e.target.value)}
        >
          <MenuItem value="Admin">Admin</MenuItem>
          <MenuItem value="Employee">Employee</MenuItem>
        </Select>
      </FormControl>
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1">Generated Username</Typography>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <TextField value={username} InputProps={{ readOnly: true }} sx={{ mr: 1 }} />
          <Button onClick={() => handleCopy(username)}><ContentCopyIcon /></Button>
        </Box>
      </Box>
      <Box sx={{ mb: 2 }}>
        <Typography variant="subtitle1">Default Password</Typography>
        <Box sx={{ display: "flex", alignItems: "center" }}>
          <TextField value={password} InputProps={{ readOnly: true }} sx={{ mr: 1 }} />
          <Button onClick={() => handleCopy(password)}><ContentCopyIcon /></Button>
        </Box>
      </Box>
      <Button
        variant="contained"
        color="primary"
        fullWidth
        onClick={handleSubmit}
        sx={{ mt: 2 }}
      >
        Submit
      </Button>
      <Button
        variant="outlined"
        color="secondary"
        fullWidth
        onClick={() => navigate(-1)}
        sx={{ mt: 1 }}
      >
        Cancel
      </Button>
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mt: 2 }}>{success}</Alert>}
    </Box>
  );
};

export default AddUser;