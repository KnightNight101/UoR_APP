// Dashboard.jsx
import React, { useState, useEffect } from "react";

const Dashboard = () => {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState({ title: "", description: "", deadline: "" });
  const [editingTask, setEditingTask] = useState(null);

  // Delete a task
  const handleDeleteTask = (id) => {
    fetch(`/api/tasks/${id}`, {
      method: "DELETE",
    })
      .then((res) => {
        if (res.ok) {
          setTasks(tasks.filter((t) => t.id !== id));
        } else {
          throw new Error("Failed to delete task");
        }
      })
      .catch((err) => console.error("Failed to delete task", err));
  };

  // Fetch tasks from backend
  useEffect(() => {
    fetch("/api/tasks")
      .then((res) => res.json())
      .then((data) => setTasks(data))
      .catch((err) => console.error("Failed to fetch tasks", err));
  }, []);

  // Handle input changes for new/edit task
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (editingTask) {
      setEditingTask({ ...editingTask, [name]: value });
    } else {
      setNewTask({ ...newTask, [name]: value });
    }
  };

  // Create a new task
  const handleCreateTask = (e) => {
    e.preventDefault();
    fetch("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newTask),
    })
      .then((res) => res.json())
      .then((created) => {
        setTasks([...tasks, created]);
        setNewTask({ title: "", description: "", deadline: "" });
      })
      .catch((err) => console.error("Failed to create task", err));
  };

  // Edit an existing task
  const handleEditTask = (task) => {
    setEditingTask({ ...task });
  };

  // Save edited task
  const handleSaveEdit = (e) => {
    e.preventDefault();
    fetch(`/api/tasks/${editingTask.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(editingTask),
    })
      .then((res) => res.json())
      .then((updated) => {
        setTasks(tasks.map((t) => (t.id === updated.id ? updated : t)));
        setEditingTask(null);
      })
      .catch((err) => console.error("Failed to update task", err));
  };

  // Cancel editing
  const handleCancelEdit = () => {
    setEditingTask(null);
  };

  return (
    <div>
      <h2>Dashboard</h2>
      {/* Task Creation Form */}
      {!editingTask && (
        <form onSubmit={handleCreateTask}>
          <input
            type="text"
            name="title"
            placeholder="Title"
            value={newTask.title}
            onChange={handleInputChange}
            required
          />
          <input
            type="text"
            name="description"
            placeholder="Description"
            value={newTask.description}
            onChange={handleInputChange}
            required
          />
          <input
            type="date"
            name="deadline"
            value={newTask.deadline}
            onChange={handleInputChange}
            required
          />
          <button type="submit">Add Task</button>
        </form>
      )}

      {/* Task Editing Form */}
      {editingTask && (
        <form onSubmit={handleSaveEdit}>
          <input
            type="text"
            name="title"
            placeholder="Title"
            value={editingTask.title}
            onChange={handleInputChange}
            required
          />
          <input
            type="text"
            name="description"
            placeholder="Description"
            value={editingTask.description}
            onChange={handleInputChange}
            required
          />
          <input
            type="date"
            name="deadline"
            value={editingTask.deadline}
            onChange={handleInputChange}
            required
          />
          <button type="submit">Save</button>
          <button type="button" onClick={handleCancelEdit}>
            Cancel
          </button>
        </form>
      )}

      {/* Task List */}
      <ul>
        {tasks.map((task) => (
          <li key={task.id}>
            <strong>{task.title}</strong>: {task.description}
            <br />
            Deadline: {task.deadline ? new Date(task.deadline).toLocaleDateString() : "No deadline"}
            <br />
            <button onClick={() => handleEditTask(task)}>Edit</button>
            <button onClick={() => handleDeleteTask(task.id)} style={{ marginLeft: "8px", color: "red" }}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Dashboard;