"""
Test script to verify apostrophe path handling works correctly.
This can be used to test the run_python_script.py launcher.

Run: python utils/run_python_script.py utils/test_apostrophe_path.py
Or:   python utils/test_apostrophe_path.py
"""
from pathlib import Path

# Test path with apostrophe
test_path = Path(r"C:\Users\edite\OneDrive - Nat'l Community Reinvestment Coaltn\Desktop\DREAM Analysis")

print("Testing apostrophe path handling...")
print(f"Path: {test_path}")
print(f"Exists: {test_path.exists()}")

if test_path.exists():
    print("SUCCESS: Path with apostrophe is accessible!")
    print(f"\nContents (first 5 items):")
    items = list(test_path.iterdir())
    for item in items[:5]:
        print(f"  - {item.name} {'(DIR)' if item.is_dir() else ''}")
    if len(items) > 5:
        print(f"  ... and {len(items) - 5} more items")
else:
    print("WARNING: Path does not exist (may need to adjust path)")

print("\n✓ Test completed successfully!")
