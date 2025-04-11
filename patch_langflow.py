import os
import sys
import shutil
import glob

def patch_langflow():
    """
    Patch Langflow by disabling Chroma-related components to avoid SQLite version issues.
    """
    base_path = os.path.dirname(os.path.abspath(__file__))
    venv_path = os.path.join(base_path, '.venv')

    print("Searching for Langflow components directory...")
    components_paths = glob.glob(f"{venv_path}/lib/python*/site-packages/langflow/components")

    if not components_paths:
        print("Langflow components directory not found in venv")
        for path in sys.path:
            comp_path = os.path.join(path, 'langflow', 'components')
            if os.path.exists(comp_path):
                components_paths = [comp_path]
                break

    if not components_paths:
        print("ERROR: Could not find Langflow components directory")
        return False

    components_path = components_paths[0]
    print(f"Found components at: {components_path}")

    print("Disabling Chroma-related components...")

    vectorstores_path = os.path.join(components_path, 'vectorstores')
    if os.path.exists(vectorstores_path):
        backup_path = os.path.join(base_path, 'vectorstores_backup')
        if not os.path.exists(backup_path):
            shutil.copytree(vectorstores_path, backup_path)
            print(f"Created backup at {backup_path}")

        chroma_files = glob.glob(f"{vectorstores_path}/*chroma*.py")

        for file_path in chroma_files:
            file_name = os.path.basename(file_path)
            print(f"Patching {file_name}...")

            with open(file_path, 'w') as f:
                f.write(
                    "# This file has been patched to avoid Chroma SQLite compatibility issues\n"
                    "from langflow.custom.component import Component\n\n"
                    "class ChromaComponent(Component):\n"
                    "    \"\"\"Dummy Chroma component to avoid SQLite version issues.\"\"\"\n"
                    "    display_name = \"Chroma\"\n"
                    "    description = \"Unavailable: SQLite version incompatible\"\n\n"
                    "    def build(self, *args, **kwargs):\n"
                    "        raise NotImplementedError(\"Chroma is not available due to SQLite version incompatibility\")\n"
                )

    for subdir in ['embeddings', 'retrievers', 'memory', 'llms', 'agents']:
        dir_path = os.path.join(components_path, subdir)
        if os.path.exists(dir_path):
            for file_path in glob.glob(f"{dir_path}/*.py"):
                with open(file_path, 'r') as f:
                    content = f.read()

                if 'chromadb' in content or 'langchain_chroma' in content:
                    backup_file = os.path.join(base_path, f"{os.path.basename(file_path)}.bak")
                    shutil.copy2(file_path, backup_file)

                    print(f"Patching references in {os.path.basename(file_path)}...")
                    modified_content = content.replace('import chromadb', '# import chromadb')
                    modified_content = modified_content.replace('from chromadb', '# from chromadb')
                    modified_content = modified_content.replace('import langchain_chroma', '# import langchain_chroma')
                    modified_content = modified_content.replace('from langchain_chroma', '# from langchain_chroma')

                    with open(file_path, 'w') as f:
                        f.write(modified_content)

    print("Patching completed successfully")
    return True

if __name__ == "__main__":
    success = patch_langflow()
    sys.exit(0 if success else 1)
