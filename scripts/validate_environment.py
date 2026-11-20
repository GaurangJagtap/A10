"""Environment validation script.

Verifies local Python version, virtual environment, and installed dependencies.
"""

import sys
import importlib

REQUIRED_PACKAGES = [
    "sklearn",
    "pandas",
    "numpy",
    "joblib",
    "pytest",
    "boto3"
]


def validate_environment():
    print(f"Python executable: {sys.executable}")
    print(f"Python version   : {sys.version.split()[0]}")

    missing = []
    print("\nChecking required packages:")
    for pkg in REQUIRED_PACKAGES:
        try:
            mod = importlib.import_module(pkg)
            version = getattr(mod, "__version__", "unknown")
            print(f"  [OK] {pkg:<15} (version: {version})")
        except ImportError:
            print(f"  [MISSING] {pkg:<15}")
            missing.append(pkg)

    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        print("Please run: pip install -r requirements.txt")
        return False

    print("\nEnvironment validation successful! All required packages are present.")
    return True


if __name__ == "__main__":
    success = validate_environment()
    sys.exit(0 if success else 1)
