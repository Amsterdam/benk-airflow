from datetime import datetime, timedelta

default_args = {
    "owner": "basis en kernregistraties",
    "depends_on_past": False,
    "start_date": datetime.utcnow(),
    "email": [
        "roel.kramer@amsterdam.nl",
        "roel.de.vries@amsterdam.nl"
    ],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(seconds=30),
}
