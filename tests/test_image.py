import pytest

from benk.image import Image


@pytest.fixture
def image():
    return Image(name="any", tag="any_tag")


class TestImage:

    def test_with_registry(self, image, monkeypatch):
        monkeypatch.setattr("benk.image.REGISTRY_URL", "any_url")

        assert image.pull_policy == "Always"
        assert image.url == "any_url/any:any_tag"

    def test_without_registry(self, image, monkeypatch):
        monkeypatch.setattr("benk.image.REGISTRY_URL", None)

        assert image.pull_policy == "Never"
        assert image.url == "any:any_tag"
