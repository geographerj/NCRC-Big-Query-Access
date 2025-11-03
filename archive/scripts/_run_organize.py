import importlib.util
from pathlib import Path

script_path = Path('_organize_pnc_files.py')
spec = importlib.util.spec_from_file_location('organize', script_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

