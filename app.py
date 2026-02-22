import importlib.util
import pathlib
import sys

# Load the real application module from the nested folder (flask-todo-app/app.py)
BASE = pathlib.Path(__file__).resolve().parent
nested_app_path = BASE / "flask-todo-app" / "app.py"

spec = importlib.util.spec_from_file_location("_inner_app", str(nested_app_path))
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)

# Expose the Flask `app` object for tests and runtime
app = getattr(module, "app")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
