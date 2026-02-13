import yaml
from pathlib import Path


def load_config(config_path: str | Path) -> dict:
    """
    Loads a YAML configuration file and returns it as a dictionary.

    Args:
        config_path: The path to the YAML file.

    Returns:
        A dictionary containing the configuration parameters.
    """
    path_obj = Path(config_path)

    if not path_obj.exists():
        raise FileNotFoundError(f"Configuration file not found at: {path_obj}")

    with open(path_obj, "r") as file:
        config = yaml.safe_load(file)

    return config