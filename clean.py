import shutil
import os
import glob

def clean():
    """Clean up build products and temporary files."""
    patterns_to_remove = [
        'build/',
        'dist/',
        '**/*.egg-info/',
        '__pycache__/',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.pytest_cache/',
        '.coverage',
        'htmlcov/',
        '.tox/',
        '.mypy_cache/',
    ]

    current_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(current_dir, '.venv')
    
    for pattern in patterns_to_remove:
        # Handle both directories and file patterns
        if pattern.endswith('/'):
            # It's a directory pattern
            # Use glob to find all matching directories
            full_pattern = os.path.join(current_dir, '**', pattern[:-1])
            matching_dirs = glob.glob(full_pattern, recursive=True)
            for dir_path in matching_dirs:
                # Skip anything in the virtual environment directory
                if venv_dir in dir_path:
                    continue
                if os.path.exists(dir_path):
                    print(f"Removing directory: {dir_path}")
                    shutil.rmtree(dir_path, ignore_errors=True)
        else:
            # It's a file pattern
            full_pattern = os.path.join(current_dir, '**', pattern)
            matching_files = glob.glob(full_pattern, recursive=True)
            for file_path in matching_files:
                # Skip anything in the virtual environment directory
                if venv_dir in file_path:
                    continue
                if os.path.exists(file_path):
                    print(f"Removing file: {file_path}")
                    os.remove(file_path)

if __name__ == "__main__":
    clean() 