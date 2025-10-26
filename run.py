#!/usr/bin/env python3
"""
Production launcher script
Usage: python run.py
"""
import os
from app import app, db

# Set production environment
os.environ['FLASK_ENV'] = 'production'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print('✓ Database initialized')
    
    print('✓ Starting Medical Tracker in production mode')
    print('✓ Server: http://0.0.0.0:5000')
    
    from waitress import serve
    serve(app, host='0.0.0.0', port=5000, threads=4)

