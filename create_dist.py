import os
import shutil
from pathlib import Path

def create_distribution():
    # Create dist directory
    dist_dir = Path('dist')
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()
    
    # Files to copy
    files_to_copy = [
        'main.py',
        'run_conversion.py',
        'run_parallel_conversion.py',
        'requirements.txt',
        'README.md',
        'setup.py',
        'TECHNICAL_DOCUMENTATION.md',
        'USER_MANUAL.md',
        'config_sample.yaml',
        'demo.py',
        'install.bat',
        'install.sh',
        '__init__.py',
        'test_tts.py'
    ]
    
    # Directories to copy
    dirs_to_copy = [
        'engines',
        'readers',
        'profiles',
        'utils',
        'config',
        'tests'
    ]
    
    # Copy files
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, dist_dir / file)
            print(f"Copied {file}")
        else:
            print(f"Warning: {file} not found")
    
    # Copy directories
    for dir_name in dirs_to_copy:
        if os.path.exists(dir_name):
            shutil.copytree(dir_name, dist_dir / dir_name)
            print(f"Copied directory {dir_name}")
        else:
            print(f"Warning: Directory {dir_name} not found")
    
    # Create zip file
    shutil.make_archive('Universal_TTS_System_Complete', 'zip', dist_dir)
    
    print("\nDistribution package created successfully!")
    print("You can find the zip file at: Universal_TTS_System_Complete.zip")
    
    # Verify contents
    print("\nVerifying contents...")
    verify_contents(dist_dir)

def verify_contents(dist_dir):
    """Verify that all necessary files and directories are present."""
    required_files = [
        'main.py',
        'run_conversion.py',
        'run_parallel_conversion.py',
        'requirements.txt',
        'README.md',
        'setup.py',
        'TECHNICAL_DOCUMENTATION.md',
        'USER_MANUAL.md',
        'config_sample.yaml',
        'demo.py',
        'install.bat',
        'install.sh',
        '__init__.py'
    ]
    
    required_dirs = [
        'engines',
        'readers',
        'profiles',
        'utils',
        'config',
        'tests'
    ]
    
    print("\nChecking required files:")
    for file in required_files:
        if (dist_dir / file).exists():
            print(f"✓ {file}")
        else:
            print(f"✗ {file} (missing)")
    
    print("\nChecking required directories:")
    for dir_name in required_dirs:
        if (dist_dir / dir_name).exists():
            print(f"✓ {dir_name}/")
        else:
            print(f"✗ {dir_name}/ (missing)")

if __name__ == "__main__":
    create_distribution()
