import platform


def what_os() -> None:
    current_os = platform.system()

    if current_os == "Windows":
        print("Running on Windows")
    elif current_os == "Linux":
        print("Running on Linux")
    elif current_os == "Darwin":
        print("Running on macOS")

    print(f"Operating System: {platform.system()}")
    print(f"OS Version: {platform.version()}")


def what_python_version() -> None:
    print(f"Python Version: {platform.python_version()}")


if __name__ == "__main__":
    what_os()
    what_python_version()
