from datetime import datetime, timedelta

default_args = {
    "owner": "basis en kernregistraties",
    "depends_on_past": False,
    "start_date": datetime.utcnow(),
    "email": [
        "roel.kramer@amsterdam.nl"
    ],  # Set this value if you want email updates on your DAG run
    "email_on_failure": False,  # Set to True if you want email updates on your DAG run
    "email_on_retry": False,  # Set to True if you want email updates on your DAG run
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}
