"""
Reliable Python script launcher that bypasses PowerShell wrapper issues.
Uses subprocess with shell=False and proper path handling.

Usage:
    python utils/run_python_script.py <script_name.py> [args...]
    
Example:
    python utils/run_python_script.py organize_pnc_onedrive_files.py
"""
import subprocess
import sys
from pathlib import Path

def run_python_script(script_path, *args):
    """
    Run a Python script using subprocess with shell=False to bypass PowerShell.
    
    Args:
        script_path: Path to the Python script to execute
        *args: Additional arguments to pass to the script
    """
    script_path = Path(script_path)
    
    if not script_path.exists():
        print(f"ERROR: Script not found: {script_path}")
        sys.exit(1)
    
    # Get the Python executable
    python_exe = sys.executable
    
    # Build command list - use list, not string, to avoid shell interpretation
    cmd = [python_exe, str(script_path)] + list(args)
    
    print(f"Executing: {' '.join(cmd)}")
    print("-" * 80)
    
    try:
        # Use subprocess with shell=False to bypass PowerShell entirely
        # This is the key: shell=False means no shell interpretation happens
        result = subprocess.run(
            cmd,
            shell=False,  # Critical: shell=False bypasses PowerShell wrapper
            check=False,  # Don't raise exception on non-zero exit
            capture_output=False,  # Show output in real-time
            text=True
        )
        
        print("-" * 80)
        if result.returncode == 0:
            print(f"✓ Script completed successfully (exit code: {result.returncode})")
        else:
            print(f"✗ Script exited with code: {result.returncode}")
            sys.exit(result.returncode)
            
    except Exception as e:
        print(f"ERROR: Could not execute script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python utils/run_python_script.py <script_name.py> [args...]")
        print("\nExample:")
        print("  python utils/run_python_script.py organize_pnc_onedrive_files.py")
        sys.exit(1)
    
    script_name = sys.argv[1]
    script_args = sys.argv[2:]
    
    # Resolve script path relative to project root
    project_root = Path(__file__).parent.parent
    script_path = project_root / script_name
    
    if not script_path.exists():
        print(f"ERROR: Script not found: {script_path}")
        sys.exit(1)
    
    run_python_script(script_path, *script_args)
