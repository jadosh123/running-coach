from pathlib import Path

def get_project_root() -> Path:
    curr = Path(__file__)
    while not any(curr.glob("*.toml")):
        curr = curr.parent

    return curr


if __name__ == "__main__":
    path = get_project_root()
    print(path)