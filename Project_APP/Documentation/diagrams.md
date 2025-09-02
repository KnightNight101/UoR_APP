# Main Py Architecture

```mermaid
flowchart TD
    A[main.py Entry Point] -->|Initializes| B[ProjectFileManager]
    A -->|Creates| C[QApplication & QQmlApplicationEngine]
    A -->|Exposes| D[QML Context Properties]
    D --> E[AuthManager]
    D --> F[DashboardManager]
    D --> G[ProjectManager]
    D --> H[UserManager]
    D --> I[LogEventBridge]
    D --> J[LoadingManager]
    C --> K[Loads Main.qml]
    K --> L[QML UI]
```

# Main Qml Architecture

```mermaid
flowchart TD
    A[ApplicationWindow] --> B[Login Page]
    A --> C[Dashboard Page]
    A --> D[Project Details Page]
    A --> E[Event Log Page]
    A --> F[Settings Page]
    C --> G["Sidebar Projects"]
    C --> H["Main Content Tasks Quadrants"]
    D --> I["Tabs Tasks Gantt Calendar Team"]
    D --> J["Right Sidebar Tab Bar"]
    D --> K["Dialogs Delete Remove Member"]
    A --> L["Backend Context Properties"]
```

# Reset Users Flow

```mermaid
flowchart TD
    Start([Start]) --> InitSession[Init DB Session]
    InitSession --> DeleteUsers[Delete users not in TARGET_USERS]
    DeleteUsers --> EnsureUsers[Ensure each TARGET_USER exists]
    EnsureUsers --> UpdatePassword[Update password and role if user exists]
    UpdatePassword --> CreateUser{User missing?}
    CreateUser -- Yes --> RegisterUser
    RegisterUser["register_user"] --> Commit[Commit changes]
    CreateUser -- No --> Commit
    Commit --> End([End])
```

# Print Users Flow

```mermaid
flowchart TD
    Start([Start]) --> GetUsers["get_all_users"]
    GetUsers --> PrintHeader["Print 'Users in database:'"]
    PrintHeader --> ForEachUser{For each user}
    ForEachUser --> PrintUser["Print user ID and Username"]
    PrintUser --> End([End])