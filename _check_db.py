import sqlite3
conn = sqlite3.connect('backend/foodstore_fresh.db')
cur = conn.cursor()

# All tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cur.fetchall()
print('ALL TABLES:')
for t in tables:
    print(f'  {t[0]}')

# User table schema
print('\n--- USER table ---')
cur.execute('PRAGMA table_info(user)')
for col in cur.fetchall():
    print(f'  {col}')

# Users data
print('\n--- USER data ---')
cur.execute('SELECT * FROM user')
for row in cur.fetchall():
    print(f'  {row}')

# Roles
for tname in ['role', 'roles', 'user_role', 'user_roles']:
    try:
        cur.execute(f'SELECT * FROM {tname}')
        print(f'\n--- {tname} ---')
        for row in cur.fetchall():
            print(f'  {row}')
    except:
        print(f'\n--- {tname}: NOT FOUND ---')

# Check user_role
cur.execute('PRAGMA table_info(user_role)')
print('\n--- user_role columns ---')
for col in cur.fetchall():
    print(f'  {col}')

cur.execute('SELECT * FROM user_role')
print('\n--- user_role data ---')
for row in cur.fetchall():
    print(f'  {row}')

# Producto, Categoria
print('\n--- Counts ---')
for table in ['producto', 'categoria', 'pedido', 'estado_pedido', 'forma_pago', 'ingrediente', 'pago', 'direccion_entrega', 'system_config']:
    try:
        cur.execute(f'SELECT COUNT(*) FROM {table}')
        print(f'{table}: {cur.fetchone()[0]} rows')
    except Exception as e:
        print(f'{table}: ERROR - {e}')

conn.close()
