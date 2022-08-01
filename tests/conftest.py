from airflow.models import Variable


def pytest_generate_tests(metafunc):
    """Set required variables to fake values."""
    variables = {
        "GRONDSLAG_DATABASE_PASSWORD": "secret_password",
        "GRONDSLAG_DATABASE_HOST": "DBXYZ.AMSTERDAM.NL",
        "GRONDSLAG_DATABASE": "peilmerken",
        "GRONDSLAG_DATABASE_USER": "userX"
    }
    for k, v in variables:
        Variable.set(k, v)

    yield

    for k, v in variables:
        Variable.delete(k, v)
