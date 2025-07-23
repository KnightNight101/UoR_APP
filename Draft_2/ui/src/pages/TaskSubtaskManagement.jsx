import React from "react";
import Container from "@mui/material/Container";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";

function TaskSubtaskManagement() {
  const [tasks, setTasks] = React.useState([]);
  const [error, setError] = React.useState("");
  React.useEffect(() => {
    fetch("/api/tasks")
      .then(res => res.json())
      .then(data => setTasks(data.tasks || []))
      .catch(() => setError("Failed to fetch tasks"));
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
            Task/Subtask Management
          </Typography>
          {error && <Typography color="error">{error}</Typography>}
          <Typography variant="body1">
            {tasks.length === 0 ? "No tasks found." : "Tasks:"}
          </Typography>
          <ul>
            {tasks.map(task => (
              <li key={task.id}>
                {task.title}
                {task.subtasks && (
                  <ul>
                    {task.subtasks.map((sub, idx) => (
                      <li key={idx}>{sub}</li>
                    ))}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </Box>
      </Container>
    </Box>
  );
}

export default TaskSubtaskManagement;