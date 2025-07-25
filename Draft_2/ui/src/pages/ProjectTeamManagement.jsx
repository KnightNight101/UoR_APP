import React from "react";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

function ProjectTeamManagement() {
  const [teams, setTeams] = React.useState([]);
  const [error, setError] = React.useState("");
  React.useEffect(() => {
    fetch("/api/teams")
      .then(res => res.json())
      .then(data => setTeams(data))
      .catch(() => setError("Failed to fetch teams"));
  }, []);
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
          {error && <Typography color="error">{error}</Typography>}
          <Typography variant="body1">
            {teams.length === 0 ? "No teams found." : "Teams:"}
          </Typography>
          <ul>
            {teams.map(team => (
              <li key={team.id}>{team.name}</li>
            ))}
          </ul>
        </Box>
      </Container>
    </Box>
  );
}

export default ProjectTeamManagement;