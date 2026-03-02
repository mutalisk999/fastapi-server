#!/usr/bin/env python
# encoding: utf-8
import bcrypt

# Test if the hashed password matches "admin123"
hashed_password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
password = "admin123"

print(f"Testing if password '{password}' matches hashed password...")
result = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
print(f"Result: {result}")

# If not, generate a new hashed password for "admin123"
if not result:
    print("\nGenerating new hashed password for 'admin123'...")
    salt = bcrypt.gensalt()
    new_hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    print(f"New hashed password: {new_hashed_password.decode('utf-8')}")
