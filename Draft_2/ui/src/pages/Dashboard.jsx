import React, { useState } from "react";
import Header from "../components/Header.jsx";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import Box from "@mui/material/Box";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemText from "@mui/material/ListItemText";
import Divider from "@mui/material/Divider";
import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import { useNavigate } from "react-router-dom";


function Dashboard() {
  const [data, setData] = useState(null);
  const [projects, setProjects] = useState([]);
  const navigate = useNavigate();

  React.useEffect(() => {
    // Fetch tasks/categories from backend
    fetch("/api/tasks")
      .then(res => res.json())
      .then(tasksData => setData(tasksData));
    // Fetch projects from backend
    fetch("/api/projects")
      .then(res => res.json())
      .then(projectsData => setProjects(projectsData));
  }, []);

  const onDragEnd = async (result) => {
    if (!data) return;
    const { destination, source, draggableId } = result;
    if (!destination) return;
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const start = data.categories[source.droppableId];
    const finish = data.categories[destination.droppableId];

    let newData;
    if (start === finish) {
      const newTaskIds = Array.from(start.taskIds);
      newTaskIds.splice(source.index, 1);
      newTaskIds.splice(destination.index, 0, draggableId);

      const newCategory = {
        ...start,
        taskIds: newTaskIds,
      };

      newData = {
        ...data,
        categories: {
          ...data.categories,
          [newCategory.id]: newCategory,
        },
      };
    } else {
      // Moving from one category to another
      const startTaskIds = Array.from(start.taskIds);
      startTaskIds.splice(source.index, 1);
      const newStart = {
        ...start,
        taskIds: startTaskIds,
      };

      const finishTaskIds = Array.from(finish.taskIds);
      finishTaskIds.splice(destination.index, 0, draggableId);
      const newFinish = {
        ...finish,
        taskIds: finishTaskIds,
      };

      newData = {
        ...data,
        categories: {
          ...data.categories,
          [newStart.id]: newStart,
          [newFinish.id]: newFinish,
        },
      };
    }
    setData(newData);
    // Persist changes to backend
    await fetch("/api/tasks/update", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newData),
    });
  };

  if (!data) {
    return <Typography>Loading...</Typography>;
  }

  return (
    <>
      <Header />
      <Box
        display="flex"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        sx={{ backgroundColor: "background.default", py: { xs: 2, md: 4 } }}
      >
        <Container
          maxWidth={false}
          sx={{
            maxWidth: "60vw",
            width: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            minHeight: "100vh",
          }}
        >
          <Box display="flex" flexDirection="column" alignItems="center" width="100%">
            <Typography variant="h4" gutterBottom>
              Dashboard
            </Typography>
            <Box sx={{ width: "100%", mb: 4 }}>
              <Typography variant="h5" gutterBottom>
                Analytics & Reporting
              </Typography>
              <Box sx={{ display: "flex", gap: 2, mb: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExport("csv")}
                >
                  Export CSV
                </Button>
                <Button
                  variant="contained"
                  color="secondary"
                  startIcon={<DownloadIcon />}
                  onClick={() => handleExport("pdf")}
                >
                  Export PDF
                </Button>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    Project Statistics
                  </Typography>
                  <TableContainer component={Paper}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Project Name</TableCell>
                          <TableCell>Tasks</TableCell>
                          <TableCell>Members</TableCell>
                          <TableCell>Created At</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {projectStats.map((stat) => (
                          <TableRow key={stat.project_id}>
                            <TableCell>{stat.name}</TableCell>
                            <TableCell>{stat.task_count}</TableCell>
                            <TableCell>{stat.member_count}</TableCell>
                            <TableCell>{stat.created_at}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle1" gutterBottom>
                    User Activity
                  </Typography>
                  <TableContainer component={Paper}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>User</TableCell>
                          <TableCell>Projects</TableCell>
                          <TableCell>Tasks</TableCell>
                          <TableCell>Joined</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {userActivity.map((user) => (
                          <TableRow key={user.user_id}>
                            <TableCell>{user.username}</TableCell>
                            <TableCell>{user.projects_count}</TableCell>
                            <TableCell>{user.tasks_count}</TableCell>
                            <TableCell>{user.created_at}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>
              </Grid>
            </Box>
            <DragDropContext onDragEnd={onDragEnd}>
              <Grid
                container
                spacing={3}
                justifyContent="center"
                alignItems="stretch"
                sx={{ width: "100%" }}
              >
                {/* Left Column: To-Do Categories */}
                <Grid item xs={12} md={8}>
                  <Box>
                    <Grid container spacing={2} direction="column">
                      {data.categoryOrder.map((categoryId) => {
                        const category = data.categories[categoryId];
                        return (
                          <Grid item key={category.id}>
                            <Paper elevation={3} sx={{ p: 2, minHeight: 200 }}>
                              <Typography variant="h6" align="center" gutterBottom>
                                {category.title}
                              </Typography>
                              <Droppable droppableId={category.id}>
                                {(provided, snapshot) => (
                                  <List
                                    ref={provided.innerRef}
                                    {...provided.droppableProps}
                                    sx={{
                                      minHeight: 100,
                                      background: snapshot.isDraggingOver ? "#f0f4ff" : "inherit",
                                      transition: "background 0.2s",
                                    }}
                                  >
                                    {category.taskIds.map((taskId, index) => {
                                      const task = data.tasks[taskId];
                                      return (
                                        <Draggable key={task.id} draggableId={task.id} index={index}>
                                          {(provided, snapshot) => (
                                            <Box
                                              ref={provided.innerRef}
                                              {...provided.draggableProps}
                                              {...provided.dragHandleProps}
                                              mb={2}
                                              sx={{
                                                background: snapshot.isDragging ? "#e3f2fd" : "#fff",
                                                borderRadius: 2,
                                                boxShadow: snapshot.isDragging ? 4 : 1,
                                              }}
                                            >
                                              <ListItem>
                                                <ListItemText
                                                  primary={task.title}
                                                  primaryTypographyProps={{ fontWeight: "bold" }}
                                                />
                                              </ListItem>
                                              <List component="div" disablePadding sx={{ pl: 3 }}>
                                                {task.subtasks.map((sub, subIdx) => (
                                                  <ListItem key={subIdx}>
                                                    <ListItemText primary={sub} />
                                                  </ListItem>
                                                ))}
                                              </List>
                                              {index < category.taskIds.length - 1 && (
                                                <Divider sx={{ mt: 1, mb: 1 }} />
                                              )}
                                            </Box>
                                          )}
                                        </Draggable>
                                      );
                                    })}
                                    {provided.placeholder}
                                  </List>
                                )}
                              </Droppable>
                            </Paper>
                          </Grid>
                        );
                      })}
                    </Grid>
                  </Box>
                </Grid>
                {/* Right Column: Projects */}
                <Grid item xs={12} md={4}>
                  <Paper
                    elevation={3}
                    sx={{
                      p: 2,
                      minHeight: 400,
                      display: "flex",
                      flexDirection: "column",
                      justifyContent: "center",
                    }}
                  >
                    <Typography variant="h6" align="center" gutterBottom>
                      Projects
                    </Typography>
                    <List>
                      {projects.map((project) => (
                        <ListItem key={project.id}>
                          <ListItemText primary={project.name} />
                        </ListItem>
                      ))}
                    </List>
                    <Box sx={{ flexGrow: 1 }} />
                    <Box sx={{ display: "flex", justifyContent: "center", mt: 2 }}>
                      <button
                        style={{
                          background: "#1976d2",
                          color: "#fff",
                          border: "none",
                          borderRadius: 4,
                          padding: "8px 16px",
                          fontWeight: "bold",
                          cursor: "pointer",
                        }}
                        onClick={() => navigate('/create-project')}
                      >
                        Create New Project
                      </button>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            </DragDropContext>
          </Box>
        </Container>
      </Box>
    </>
  );
}

export default Dashboard;