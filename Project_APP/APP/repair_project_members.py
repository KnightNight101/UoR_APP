import sys
sys.path.insert(0, 'Draft_2/app')
from db import SessionLocal, Project, ProjectMember

s = SessionLocal()
fixed = 0
for p in s.query(Project).all():
    exists = s.query(ProjectMember).filter_by(project_id=p.id, user_id=p.owner_id).first()
    if not exists:
        s.add(ProjectMember(project_id=p.id, user_id=p.owner_id, role='owner'))
        fixed += 1
s.commit()
print(f'Added {fixed} missing owner memberships.')
s.close()