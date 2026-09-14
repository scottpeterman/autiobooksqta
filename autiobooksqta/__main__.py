# autiobooksqta/__main__.py

import os
import importlib.util
import subprocess
import sys
import pkg_resources


def install_bundled_model():
    """Install the bundled spaCy model if not already installed."""
    # Check if the model is already installed
    if importlib.util.find_spec("en_core_web_sm") is None:
        try:
            # Get the path to the bundled wheel file
            model_path = pkg_resources.resource_filename(
                'autiobooksqta', 'models/en_core_web_sm-3.8.0-py3-none-any.whl'
            )

            if os.path.exists(model_path):
                print("Installing bundled spaCy model...")
                subprocess.check_call([
                    sys.executable,
                    "-m", "pip", "install",
                    model_path
                ])
                print("spaCy model installed successfully!")
            else:
                print("Warning: Bundled spaCy model not found at:", model_path)
        except Exception as e:
            print(f"Error installing bundled spaCy model: {e}")


# Main entry point
def main():
    # Install the model before importing other modules that might need it
    install_bundled_model()

    # Import your main application module
    from .autiobookspqt import main as app_main

    # Run the application
    app_main()


if __name__ == "__main__":
    main()