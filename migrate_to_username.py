"""
Migration script to add username field to existing users
Run this once to update existing database

Note: This will recreate the database if the username column doesn't exist.
Existing users without usernames will be assigned usernames based on their email.
"""
from app import app
from models import db, User

with app.app_context():
    # Get database path
    import os
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    if os.path.exists(db_path):
        print(f"Found database at: {db_path}")
        
        # Check if username column exists
        result = db.engine.execute("PRAGMA table_info(user)")
        columns = [row[1] for row in result]
        
        if 'username' not in columns:
            print("Username column not found. Adding username to existing users...")
            
            # Get all existing users
            existing_users = User.query.all()
            
            if existing_users:
                print(f"Found {len(existing_users)} existing users.")
                
                # First, add username column with default values (SQLite will allow NULL temporarily)
                try:
                    db.engine.execute("ALTER TABLE user ADD COLUMN username VARCHAR(80)")
                    print("Added username column.")
                except Exception as e:
                    print(f"Could not add username column: {e}")
                
                # Update existing users with usernames
                for user in existing_users:
                    if not user.username:
                        # Generate username from email
                        if '@' in user.email:
                            username = user.email.split('@')[0]
                        else:
                            username = f"user_{user.id}"
                        
                        # Make sure username is unique
                        counter = 1
                        base_username = username
                        while User.query.filter_by(username=username).first():
                            username = f"{base_username}{counter}"
                            counter += 1
                        
                        user.username = username
                        db.session.add(user)
                        print(f"Added username '{username}' to user {user.id} ({user.email})")
                
                db.session.commit()
                
                # Now make username NOT NULL by recreating table
                print("Recreating table with NOT NULL constraint...")
                
                db.engine.execute("""
                    CREATE TABLE user_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(80) NOT NULL UNIQUE,
                        email VARCHAR(120) NOT NULL UNIQUE,
                        name VARCHAR(120) NOT NULL,
                        role VARCHAR(20) NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Copy all data
                users = User.query.all()
                for user in users:
                    db.engine.execute("""
                        INSERT INTO user_new (id, username, email, name, role, password_hash, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (user.id, user.username, user.email, user.name, user.role, user.password_hash, user.created_at))
                
                db.engine.execute("DROP TABLE user")
                db.engine.execute("ALTER TABLE user_new RENAME TO user")
                print("Table recreated successfully!")
            else:
                print("No existing users found.")
                
                # Just drop and recreate empty table
                db.engine.execute("DROP TABLE IF EXISTS user")
                db.create_all()
                print("Created new user table with username field.")
        else:
            print("Username column already exists. Migration not needed.")
    else:
        print("Database not found. Creating new database with username field...")
        db.create_all()
        print("New database created!")
    
    print("\nMigration complete!")
    print("You can now use usernames for login.")

