
def install_and_import(package: str, version: str):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package + version])
    finally:
        globals()[package] = importlib.import_module(package)


# Can we install this in airflow during setup?
install_and_import("pydantic", "~=1.10.0")
