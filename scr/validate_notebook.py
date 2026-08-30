"""Execute the public notebook in memory from the repository root."""

import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    notebook_path = root / "data_visualization.ipynb"
    notebook = nbformat.read(notebook_path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=300,
        kernel_name=os.environ.get("NOTEBOOK_KERNEL", "python3"),
        resources={"metadata": {"path": str(root)}},
    )
    client.execute()
    print(f"Validated {notebook_path.name}: {len(notebook.cells)} cells executed in memory")


if __name__ == "__main__":
    main()
