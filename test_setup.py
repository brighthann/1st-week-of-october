"""Test script to verify setup."""
import sys
import importlib


def test_imports():
    """Test that all required packages can be imported."""
    packages = [
        "fastapi",
        "streamlit",
        "aiohttp",
        "sqlalchemy",
        "prometheus_client",
        "plotly",
        "pandas",
    ]
    failed_imports = []

    for package in packages:
        try:
            importlib.import_module(package)
            print(f" {package} imported successfully")
        except ImportError as e:
            print(f" Failed to import {package}: {e}")
            failed_imports.append(package)

    if failed_imports:
        print(f"\n Setup incomplete. Failed imports: {failed_imports}")
        return False
    else:
        print("\n All packages imported successfully! Setup is complete.")
        return True


if __name__ == "__main__":
    print(f"Python version: {sys.version}")
    print("Testing package imports...\n")

    success = test_imports()
    sys.exit(0 if success else 1)
