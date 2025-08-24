from Draft_2.app.db import get_all_users, get_user_projects, get_project_by_id, add_project_member, SessionLocal, Project, User, ProjectMember

def assign_all_users_to_all_projects():
    with SessionLocal() as session:
        users = session.query(User).all()
        projects = session.query(Project).all()
        for project in projects:
            for user in users:
                # Check if user is already a member
                exists = session.query(ProjectMember).filter_by(project_id=project.id, user_id=user.id).first()
                if not exists:
                    pm = ProjectMember(project_id=project.id, user_id=user.id, role='member')
                    session.add(pm)
        session.commit()
    print(f"Assigned {len(users)} users to {len(projects)} projects (if not already assigned).")

if __name__ == "__main__":
    assign_all_users_to_all_projects()
def print_user_project_memberships():
    from Draft_2.app.db import SessionLocal, User, Project, ProjectMember
    with SessionLocal() as session:
        users = session.query(User).all()
        for user in users:
            memberships = session.query(ProjectMember).filter(ProjectMember.user_id == user.id).all()
            project_ids = [m.project_id for m in memberships]
            projects = session.query(Project).filter(Project.id.in_(project_ids)).all() if project_ids else []
            print(f"User: {user.username} (id={user.id})")
            if projects:
                for p in projects:
                    print(f"  - Project: {p.name} (id={p.id})")
            else:
                print("  - No projects assigned")