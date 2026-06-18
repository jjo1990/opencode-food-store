from argon2 import PasswordHasher
from argon2.exceptions import InvalidHash, VerifyMismatchError, VerificationError

ph = PasswordHasher()

# Hash from DB
stored = "$argon2id$v=19$m=65536,t=3,p=4$3udYZ5nPLZrq/f/nrHnk0g$3KTXKsCh54fvyUV1IspaL92sfD+cgvEefHShMBzcAcg"

print(f"Stored hash: {stored}")
print(f"Hash length: {len(stored)}")

print("\nAttempting verify with 'admin123'...")
try:
    result = ph.verify(stored, "admin123")
    print(f"Result: {result}")
except VerifyMismatchError as e:
    print(f"WRONG PASSWORD: {e}")
except VerificationError as e:
    print(f"VERIFICATION ERROR: {e}")
except InvalidHash as e:
    print(f"INVALID HASH: '{e}'")
except Exception as e:
    print(f"OTHER ERROR: {type(e).__name__}: {e}")

# Test what a fresh hash looks like
print("\n--- Fresh hash ---")
fresh = ph.hash("admin123")
print(f"Fresh: {fresh}")
print(f"Fresh len: {len(fresh)}")

# Try verifying fresh
print("\nVerifying fresh...")
try:
    result = ph.verify(fresh, "admin123")
    print(f"OK: {result}")
except Exception as e:
    print(f"Error: {e}")
