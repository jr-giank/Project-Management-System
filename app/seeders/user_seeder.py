
from app.models.users import User, Role
from app.extensions import db

def seed_users():

    manager_user = User(
        first_name="Manager",
        last_name="User",
        email="test-manager@example.com",
        role=Role.manager,
        password="SecureP@ssword1"
    )
    
    employee_user = User(
        first_name="Employee",
        last_name="User",
        email="test-employee@example.com",
        role=Role.employee,
        password="SecureP@ssword1"
    )

    db.session.add(manager_user)
    db.session.add(employee_user)
    db.session.commit()

    print("\nDB seeded successfully\n")