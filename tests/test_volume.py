import pytest

from benk.volume import Volume


@pytest.fixture
def volume():
    return Volume(name="any", mount_path="any_path", claim="any_claim")


class TestVolume:

    def test_init(self, volume):
        assert volume.v1mount.name == "any"
        assert volume.v1mount.mount_path == "any_path"

        assert volume.v1volume.name == "any"
        assert volume.v1volume.persistent_volume_claim.claim_name == "any_claim"
