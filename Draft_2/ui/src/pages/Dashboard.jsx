import React, { useState } from "react";
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

const initialData = {
  categories: {
    urgent_important: {
      id: "urgent_important",
      title: "Urgent and Important",
      taskIds: ["task-1", "task-2"],
    },
    urgent: {
      id: "urgent",
      title: "Urgent",
      taskIds: ["task-3"],
    },
    important: {
      id: "important",
      title: "Important",
      taskIds: ["task-4"],
    },
    others: {
      id: "others",
      title: "Others",
      taskIds: ["task-5"],
    },
  },
  tasks: {
    "task-1": {
      id: "task-1",
      title: "Finish report",
      subtasks: ["Draft", "Review"],
    },
    "task-2": {
      id: "task-2",
      title: "Prepare slides",
      subtasks: ["Outline", "Design"],
    },
    "task-3": {
      id: "task-3",
      title: "Reply to urgent emails",
      subtasks: ["Client A", "Manager"],
    },
    "task-4": {
      id: "task-4",
      title: "Plan next sprint",
      subtasks: ["Backlog grooming"],
    },
    "task-5": {
      id: "task-5",
      title: "Read industry news",
      subtasks: ["AI trends"],
    },
  },
  categoryOrder: [
    "urgent_important",
    "urgent",
    "important",
    "others",
  ],
};

function Dashboard() {
  const [data, setData] = useState(initialData);

  const onDragEnd = (result) => {
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

    if (start === finish) {
      const newTaskIds = Array.from(start.taskIds);
      newTaskIds.splice(source.index, 1);
      newTaskIds.splice(destination.index, 0, draggableId);

      const newCategory = {
        ...start,
        taskIds: newTaskIds,
      };

      setData({
        ...data,
        categories: {
          ...data.categories,
          [newCategory.id]: newCategory,
        },
      });
      return;
    }

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

    setData({
      ...data,
      categories: {
        ...data.categories,
        [newStart.id]: newStart,
        [newFinish.id]: newFinish,
      },
    });
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      sx={{ backgroundColor: "background.default", py: { xs: 2, md: 4 } }}
    >
      <Container
        maxWidth="lg"
        sx={{
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
                    <ListItem>
                      <ListItemText primary="Project Alpha" />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="Project Beta" />
                    </ListItem>
                    <ListItem>
                      <ListItemText primary="Project Gamma" />
                    </ListItem>
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
  );
}

export default Dashboard;