import pytest
from starlette import status

from modal_backend.settings import get_settings

url: str = "/notification"
settings = get_settings()


@pytest.mark.parametrize("status_code, ", [(status.HTTP_200_OK,)])
def test_get_notes(status_code):
    pass
