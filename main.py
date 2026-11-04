import importlib
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: uv run main.py <lab_name>")
        sys.exit(1)

    lab_name = sys.argv[1]

    try:
        module = importlib.import_module(f"{lab_name}.main")
        module.main()
    except ModuleNotFoundError:
        print(f"Lab '{lab_name}' not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
