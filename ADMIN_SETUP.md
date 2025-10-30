# Admin Setup Guide

## What's New

### Features Added:
1. **Username-based login** - Users can now login with either username or email
2. **Admin role** - New admin role for user management
3. **Admin dashboard** - Complete user management interface
4. **User management** - Admins can view, edit, delete users, and reset passwords

### Changes Made:
- User model now includes `username` field
- Login supports both username and email
- Registration requires username
- New admin dashboard at `/admin/dashboard`
- Admin can manage all users at `/admin/users/<user_id>`

---

## Setting Up Admin User

### Option 1: Via Python Script (Recommended for existing databases)

```bash
# Run the migration to add username field
python migrate_to_username.py

# Create an admin user
python
```

Then in Python:
```python
from app import app
from models import db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create admin user
    admin = User(
        username='admin',
        email='admin@medical.com',
        name='Admin User',
        role='admin',
        password_hash=generate_password_hash('admin123')  # Change this!
    )
    
    db.session.add(admin)
    db.session.commit()
    print("Admin user created!")
```

### Option 2: Register First, Then Change Role

1. Register a new user through the web interface
2. Run the migration:
   ```bash
   python migrate_to_username.py
   ```
3. Change the user to admin in Python:

```python
from app import app
from models import db, User

with app.app_context():
    user = User.query.filter_by(email='your@email.com').first()
    user.role = 'admin'
    db.session.commit()
    print("User promoted to admin!")
```

---

## Admin Dashboard Features

### Access:
- URL: `/admin/dashboard`
- Shows statistics: Total users, Patients, Doctors, Admins
- Lists all users in a table

### User Management:
1. **View/Edit User**: Click "View/Edit" on any user
   - Change username, name, email
   - Change role (patient/doctor/admin)
   - Reset password

2. **Delete User**: Click "Delete" button
   - Requires confirmation
   - Prevents self-deletion

3. **Password Reset**: 
   - Admins can reset any user's password
   - New password must be at least 6 characters

---

## Login Instructions

Users can now login with either:
- **Username**: `admin`
- **Email**: `admin@medical.com`

Both methods work with the same password.

---

## Security Notes

1. **Admin Protection**: 
   - Admins cannot delete themselves
   - Admins cannot change their own admin role

2. **Password Security**:
   - Minimum 6 characters
   - Passwords are hashed using Werkzeug

3. **User Validation**:
   - Usernames must be unique
   - Emails must be unique
   - Input sanitization on all fields

---

## Testing on Oracle Server

After pulling the latest code:

```bash
# SSH into Oracle server
ssh ubuntu@129.154.41.255 -i your-key.key

cd ~/med

# Pull latest changes
git pull origin main

# Run migration if needed
python3 migrate_to_username.py

# Restart the app
sudo systemctl restart medical-tracker

# Check logs
sudo journalctl -u medical-tracker -n 50 -f
```

---

## Troubleshooting

### "Username already exists" error:
- This means the username is already taken
- Choose a different username during registration

### "Database migration failed":
- Make a backup first: `cp medical_app.db medical_app.db.backup`
- Delete the database to start fresh: `rm medical_app.db`
- Rerun the app: `python app.py`

### Can't see admin dashboard:
- Make sure the user role is set to 'admin' in the database
- Check browser console for errors
- Verify user is logged in

---

## For Fresh Installation

If setting up from scratch:

```bash
# Clone the repo
git clone https://github.com/Sirfaviaz/med.git
cd med

# Install dependencies
pip install -r requirements.txt

# Run the app (creates database automatically)
python app.py

# Create first admin user (in another terminal)
python -c "
from app import app
from models import db, User
from werkzeug.security import generate_password_hash
with app.app_context():
    admin = User(
        username='admin',
        email='admin@medical.com',
        name='Admin',
        role='admin',
        password_hash=generate_password_hash('admin123')
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin created!')
"
```

Now you can login with username `admin` or email `admin@medical.com`!

