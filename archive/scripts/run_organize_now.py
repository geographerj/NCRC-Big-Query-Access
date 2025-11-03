"""
Execute organize_pnc_files_DIRECT.py using importlib to bypass terminal wrapper.
This loads and executes the module directly, same pattern as goal_setting_analysis_main.py
"""
import importlib.util
import sys
from pathlib import Path

def load_module_from_path(module_name, file_path):
    """Load a Python module from file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load and execute the organize script
script_path = Path(__file__).parent / 'organize_pnc_files_DIRECT.py'

if not script_path.exists():
    print(f"ERROR: Script not found: {script_path}")
    sys.exit(1)

print("Executing file organization script...")
print("=" * 80)

try:
    # Load and execute - this will run all code at module level
    module = load_module_from_path('organize_pnc_direct', script_path)
    print("\n" + "=" * 80)
    print("Execution completed successfully!")
except KeyboardInterrupt:
    print("\n\nExecution cancelled by user")
    sys.exit(1)
except Exception as e:
    print(f"\nERROR during execution: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

