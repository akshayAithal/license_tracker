#!/usr/bin/env python
"""Script to generate 100 test users"""

import random
import string
from hashlib import sha256

# Generate 100 users
users = []
for i in range(1, 101):
    username = f"user{i:03d}"
    # Generate a simple password
    password = "password123"
    # Hash the password (same as in the registration endpoint)
    password_hash = sha256(password.encode()).hexdigest()
    
    # Random first and last names
    first_names = ["John", "Jane", "Mike", "Sarah", "David", "Emma", "Chris", "Lisa", "Tom", "Amy",
                   "James", "Mary", "Robert", "Patricia", "Michael", "Jennifer", "William", "Linda",
                   "Richard", "Elizabeth", "Joseph", "Barbara", "Thomas", "Susan", "Charles", "Jessica"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
                  "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
                  "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    email = f"{username.lower()}@example.com"
    
    # Alternate between admin and non-admin users (10% admins)
    is_admin = i <= 10
    
    users.append({
        'login_name': username,
        'password': password_hash,
        'first_name': first_name,
        'last_name': last_name,
        'mail_id': email,
        'is_admin': is_admin
    })

# Create SQL insert statements
sql = "-- Insert 100 test users\n"
sql += "-- All users have password: password123\n"
sql += "-- Users 001-010 are admins\n\n"

sql += "INSERT INTO users (login_name, password, first_name, last_name, mail_id, is_admin, created_at, updated_at) VALUES\n"

for i, user in enumerate(users):
    sql += f"('{user['login_name']}', '{user['password']}', '{user['first_name']}', '{user['last_name']}', '{user['mail_id']}', {1 if user['is_admin'] else 0}, NOW(), NOW())"
    if i < len(users) - 1:
        sql += ",\n"
    else:
        sql += ";\n"

# Write to SQL file
with open('c:\\license_tracker\\init-db\\06-test-users.sql', 'w') as f:
    f.write(sql)

print(f"Generated SQL file with {len(users)} users")
print(f"Admin users: user001 - user010 (password: password123)")
print(f"Regular users: user011 - user100 (password: password123)")
