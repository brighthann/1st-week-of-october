#  creates __init__.py files for all Python packages.
# This script creates empty __init__.py files in all directories that need them. to make them importable python packages

#  terminal command for running script:  python create_init.py

# import os
from pathlib import Path

# Directories that need __init__.py files
PACKAGE_DIRECTORIES = [
    "src",
    "src/api",
    "src/api/endpoints",
    "src/api/services",
    "src/models",
    "src/config",
    "src/dashboard",
    "src/dashboard/components",
    "tests",
]


def create_init_files():
    # """Create __init__.py files in all package directories."""
    created_count = 0
    already_exists_count = 0

    print("Creating __init__.py files for Python packages...\n")

    for directory in PACKAGE_DIRECTORIES:
        # Create directory if it doesn't exist
        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)

        # Create __init__.py file
        init_file = dir_path / "__init__.py"

        if init_file.exists():
            print(f"{init_file} already exists")
            already_exists_count += 1
        else:
            # Create empty __init__.py file
            init_file.touch()
            print(f"Created {init_file}")
            created_count += 1

    # Print summary
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"Created: {created_count} file(s)")
    print(f"Already existed: {already_exists_count} file(s)")
    print(f"Total packages: {len(PACKAGE_DIRECTORIES)}")
    print(f"{'='*60}")

    if created_count > 0:
        print("\n All __init__.py files created successfully!")
    else:
        print("\n All __init__.py files already exist!")

    # Verify imports work
    print("\n Verifying Python can recognize packages...")
    try:
        import src
        import src.api
        import src.config
        import src.models
        import tests

        print("All packages are importable!\n")
        return True
    except ImportError as e:
        print(f"Import verification failed: {e}\n")
        return False


def list_created_files():
    """List all __init__.py files in the project."""
    print("\n __init__.py files in project:")
    print(f"{'='*60}")

    init_files = list(Path(".").rglob("__init__.py"))

    # Exclude venv and other irrelevant directories
    init_files = [
        f
        for f in init_files
        if "venv" not in str(f) and "env" not in str(f) and ".eggs" not in str(f)
    ]

    for init_file in sorted(init_files):
        size = init_file.stat().st_size
        print(f"{init_file} ({size} bytes)")

    print(f"{'='*60}")
    print(f"Total: {len(init_files)} file(s)\n")


if __name__ == "__main__":
    print("=" * 60)
    print("  Python Package Initializer - DashMonitor Project")
    print("=" * 60)
    print()

    # Create the files
    success = create_init_files()

    # List all __init__.py files
    list_created_files()

    # Exit with appropriate code
    exit(0 if success else 1)
