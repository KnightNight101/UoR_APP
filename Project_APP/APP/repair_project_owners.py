import sys
sys.path.insert(0, 'Draft_2/app')
from db import SessionLocal, Project, ProjectMember

s = SessionLocal()
updated_projects = 0
updated_members = 0

# Update Project.owner_id
for p in s.query(Project).filter_by(owner_id=0).all():
    p.owner_id = 2
    updated_projects += 1

# Update ProjectMember.user_id
for pm in s.query(ProjectMember).filter_by(user_id=0).all():
    pm.user_id = 2
    updated_members += 1

s.commit()
print(f'Updated {updated_projects} projects and {updated_members} project members to user_id=2.')
s.close()