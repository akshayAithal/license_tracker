#!/usr/bin/env python3
from werkzeug.security import generate_password_hash

h = generate_password_hash('password123')
lines = []
for i in range(1, 101):
    login = 'user{:03d}'.format(i)
    email = '{}@example.com'.format(login)
    t = 'ADMIN' if i <= 10 else 'USER'
    lines.append("('{}', '{}', '{}', '{}', 1, NOW(), NOW())".format(login, email, h, t))

sql = 'INSERT IGNORE INTO local_users (login, email, password_hash, type, is_active, created_at, updated_at) VALUES\n' + ',\n'.join(lines) + ';'
with open('/tmp/test_users.sql', 'w') as f:
    f.write(sql)
print('Generated /tmp/test_users.sql with 100 users')
