import os

# Check if __init__.py exists, and create it if it doesn't
init_path = os.path.join(os.path.dirname(__file__), "__init__.py")
if not os.path.exists(init_path):
    with open(init_path, "w") as f:
        pass
