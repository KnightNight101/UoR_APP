# PyQt Project Management App

A cross-platform project management application built with Python and PyQt5, supporting projects, tasks, subtasks, dependencies, team management, and Gantt chart visualization.

---

## Features

- User authentication and role-based access
- Project creation, editing, and deletion
- Task and subtask management with dependencies
- Team member assignment and roles
- Gantt chart visualization for project timelines
- Messaging between users
- File uploads per project/task
- Calendar and event tracking

---

## Setup Instructions

### 1. Clone the Repository

```sh
git clone https://github.com/yourusername/your-repo.git
cd your-repo/Draft_2/app
```

### 2. Install Python Dependencies

It is recommended to use a virtual environment:

```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r ../requirements.txt
```

### 3. Initialize the Database

The database will auto-initialize on first run. To manually initialize or reset:

```sh
python db.py
```

### 4. Run the Application

```sh
python main.py
```

The app will launch in a maximized window.

---

## Usage Notes

- Default admin user: `admin` / `admin123`
- All data is stored in `auth.db` in the `Draft_2/app` directory.
- To reset the database, delete `auth.db` and rerun the app.
- For development, edit code in `Draft_2/app/main.py` and `Draft_2/app/db.py`.

---

## Troubleshooting

- If you encounter missing dependencies, ensure you have Python 3.8+ and run `pip install -r requirements.txt`.
- For database errors, delete `auth.db` and restart.
- For UI issues, ensure PyQt5 is installed and your Python environment is activated.

---

## Contributing

1. Fork the repository and create a feature branch.
2. Make your changes with clear comments.
3. Submit a pull request with a description of your changes.

---

## License

MIT License
