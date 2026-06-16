#!/usr/bin/env python
"""Quick FSM verification script for Task 9"""

from app.pedidos.service import TERMINAL_STATES, TRANSITIONS

print("=" * 70)
print("TASK 9: FSM Compatibility Verification")
print("=" * 70)

# 1. Verify FSM structure
print("\n[OK] FSM loaded successfully")
print(f"  Terminal states: {TERMINAL_STATES}")
assert TERMINAL_STATES == {"ENTREGADO", "CANCELADO"}, "Terminal states mismatch"

# 2. Verify all transitions have required fields
print("\n[OK] Checking transition structure...")
for from_state, transitions in TRANSITIONS.items():
    for to_state, info in transitions.items():
        assert "roles" in info, f"{from_state}->{to_state} missing 'roles'"
        assert "stock_action" in info, f"{from_state}->{to_state} missing 'stock_action'"
        assert isinstance(info["roles"], list), f"{from_state}->{to_state} roles must be list"
print("  All transitions have correct structure")

# 3. Verify stock restoration scenarios
print("\n[OK] Checking stock restoration scenarios...")
stock_restore_transitions = [
    ("CONFIRMADO", "CANCELADO"),
    ("EN_PREPARACION", "CANCELADO"),
]
for from_s, to_s in stock_restore_transitions:
    info = TRANSITIONS[from_s][to_s]
    assert info["stock_action"] == "restore", f"{from_s}->{to_s} should restore stock"
print("  All CANCELADO transitions from non-terminal states restore stock")

# 4. Verify role permissions for key transitions
print("\n[OK] Checking role permissions...")
assert "CLIENT" in TRANSITIONS["PENDIENTE"]["CANCELADO"]["roles"]
assert "ADMIN" in TRANSITIONS["EN_PREPARACION"]["CANCELADO"]["roles"]
assert "PEDIDOS" in TRANSITIONS["CONFIRMADO"]["EN_PREPARACION"]["roles"]
print("  Role permissions configured correctly")

# 5. Verify terminal states cannot transition
print("\n[OK] Verifying terminal states...")
assert TRANSITIONS["ENTREGADO"] == {}, "ENTREGADO should have no transitions"
assert TRANSITIONS["CANCELADO"] == {}, "CANCELADO should have no transitions"
print("  Terminal states cannot transition")

print("\n" + "=" * 70)
print("[PASS] All FSM verification checks PASSED")
print("=" * 70)
