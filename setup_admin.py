"""
Quick setup script to create admin user and fix database schema
Run this on your Oracle server or locally
"""
from app import app
from models import db, User
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect

def check_table_schema():
    """Check if username column exists in user table"""
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('user')]
        return 'username' in columns
    except:
        return False

def create_admin(username='admin', email='admin@medical.com', password='admin123'):
    """Create admin user"""
    with app.app_context():
        # Check if table has username column
        if not check_table_schema():
            print("❌ Database schema doesn't have username column.")
            print("Running migration...")
            try:
                # Try to add username column
                db.engine.execute("ALTER TABLE user ADD COLUMN username VARCHAR(80)")
                print("✓ Added username column")
                
                # Get all users and set username
                users = User.query.all()
                for user in users:
                    if not hasattr(user, 'username') or not user.username:
                        # Generate username from email
                        if '@' in user.email:
                            gen_username = user.email.split('@')[0]
                        else:
                            gen_username = f"user_{user.id}"
                        
                        # Make unique
                        counter = 1
                        base_username = gen_username
                        while User.query.filter_by(username=gen_username).first():
                            gen_username = f"{base_username}{counter}"
                            counter += 1
                        
                        db.session.execute("UPDATE user SET username = ? WHERE id = ?", (gen_username, user.id))
                        print(f"  Set username for user {user.id}: {gen_username}")
                
                db.session.commit()
            except Exception as e:
                print(f"⚠ Error during migration: {e}")
                print("Dropping and recreating database...")
                db.drop_all()
                db.create_all()
                print("✓ Database recreated with new schema")
        
        # Check if admin user exists
        existing_admin = User.query.filter_by(username=username).first()
        
        if existing_admin:
            # Update existing admin
            existing_admin.email = email
            existing_admin.name = 'Admin User'
            existing_admin.role = 'admin'
            existing_admin.password_hash = generate_password_hash(password)
            db.session.commit()
            print(f"✓ Updated existing admin user '{username}'")
        else:
            # Create new admin
            admin = User(
                username=username,
                email=email,
                name='Admin User',
                role='admin',
                password_hash=generate_password_hash(password)
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Created admin user '{username}'")
        
        # List all admins
        admins = User.query.filter_by(role='admin').all()
        print("\n📋 All admin users:")
        for admin in admins:
            print(f"  - Username: {admin.username}, Email: {admin.email}, ID: {admin.id}")
        
        print("\n✓ Admin setup complete!")
        print("\nYou can now login with:")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print(f"  Password: {password}")
        print("\n⚠️  Remember to change the password after first login!")

if __name__ == '__main__':
    import sys
    
    # Parse command line arguments
    if len(sys.argv) >= 4:
        username = sys.argv[1]
        email = sys.argv[2]
        password = sys.argv[3]
    else:
        username = 'admin'
        email = 'admin@medical.com'
        password = 'admin123'
    
    print("🔧 Admin Setup Script")
    print("=" * 50)
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    print("=" * 50)
    print()
    
    try:
        create_admin(username, email, password)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

