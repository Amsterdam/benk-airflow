import datetime as dt
import os
from tempfile import TemporaryDirectory
import paramiko
from paramiko.sftp_client import SFTPClient

CONFIG_IBZ = {
    "username": os.environ["SFTP_IBURGERZAKEN_UID"],
    "password": os.environ["SFTP_IBURGERZAKEN_UID_PWD"],
    "host": os.environ["DB_IBURGERZAKEN_SERVER"],
    "port": "22"
}

CONFIG_GOB = {
    "username": f'{os.environ["GOB_OBJECTSTORE_TENANTID"]}:{os.environ["GOB_OBJECTSTORE_USER"]}',
    "password": os.environ["GOB_OBJECTSTORE_PWD"],
    "host": "ftp.objectstore.eu",
    "port": "22"
}


def _get_client(username: str, password: str, host: str, port: str) -> SFTPClient:
    transport = paramiko.Transport((host, int(port)))
    transport.connect(username=username, password=password)
    print(f"Connected to {username}@{host}")
    return paramiko.SFTPClient.from_transport(transport)


def sync_files():
    with (
        _get_client(**CONFIG_IBZ) as ibz_client,
        _get_client(**CONFIG_GOB) as gob_client,
        TemporaryDirectory() as tempdir
    ):
        now = dt.datetime.now().strftime("%Y%m%d_%H%M")

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

            gob_client.put(tmp_file, f"development/iburgerzaken/{now}/{item}")
            print("Uploaded:", item)


if __name__ == '__main__':
    sync_files()
