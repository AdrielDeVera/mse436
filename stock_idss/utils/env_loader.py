import os
from dotenv import load_dotenv

def get_env_variable(key: str) -> str:
    """
    Load the value of an environment variable from .env file.
    Args:
        key (str): The environment variable key to retrieve.
    Returns:
        str: The value of the environment variable.
    Raises:
        KeyError: If the key is not found in the environment.
    """
    load_dotenv()
    value = os.getenv(key)
    if value is None:
        raise KeyError(f"Environment variable '{key}' not found in .env file.")
    return value

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Get environment variable from .env file.")
    parser.add_argument("key", type=str, help="Environment variable key")
    args = parser.parse_args()
    try:
        print(get_env_variable(args.key))
    except KeyError as e:
        print(e)
