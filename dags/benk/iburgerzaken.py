from datetime import datetime

from airflow.decorators import dag, task

from benk.common import NAMESPACE, TEAM_NAME


operator_default_args = {
    "labels": {"team_name": TEAM_NAME},
    "in_cluster": True,
    "get_logs": True,
    "hostnetwork": True,
    "log_events_on_failure": True,
    "reattach_on_restart": False,
    "do_xcom_push": False,
}


CONFIG_IBZ = {
    "host": "{{ var.value.get('db-iburgerzaken-server') }}",
    "port": 22,
    "user": "{{ var.value.get('sftp-iburgerzaken-uid') }}",
    "pw": "{{ var.value.get('sftp-iburgerzaken-uid-pwd') }}"
}
CONFIG_GOB = {
    "host": "{{ var.value.get('db-iburgerzaken-server') }}",
    "port": 22,
    "user": "{{ var.value.get('objectstore-gob-tenantid') }}:{{ var.value.get('objectstore-gob-user') }}",
    "pw": "{{ var.value.get('objectstore-gob-password') }}"
}


@dag(
    schedule_interval=None,
    catchup=False,
    start_date=datetime.utcnow(),
    tags=["pink", "brp", "iburgerzaken"],
)
def transfer_ibz_to_gob():
    """Main DAG."""

    @task.kubernetes(
        name="list_contents",
        namespace=NAMESPACE,
        image="python:3.10-slim-bullseye",
        **operator_default_args,
    )
    def transfer_files():
        import subprocess
        import sys
        import datetime as dt
        import os
        from tempfile import TemporaryDirectory

        subprocess.check_call([sys.executable, "-m", "pip", "install", "paramiko"])

        import paramiko
        from paramiko.sftp_client import SFTPClient

        def get_connection(user, pw, host, port) -> SFTPClient:
            transport = paramiko.Transport((host, int(port)))
            transport.connect(username=user, password=pw)
            print(f"Connected to {user}@{host}")
            return paramiko.SFTPClient.from_transport(transport)

        with (
            get_connection(**CONFIG_IBZ) as ibz_client,
            get_connection(**CONFIG_GOB) as gob_client,
            TemporaryDirectory() as tempdir
        ):
            for item in ibz_client.listdir():
                stat = ibz_client.stat(item)

                print(
                    item,
                    f"{stat.st_size / 1024 / 1024:,.1f} mb",
                    dt.datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                )
                tmp_file = os.path.join(tempdir, item)

                ibz_client.get(item, tmp_file)
                print("Downloaded:", item)

                gob_client.put(tmp_file, f"development/iburgerzaken/{item}")
                print("Uploaded:", item)

    transfer_files()


transfer_ibz_to_gob()
