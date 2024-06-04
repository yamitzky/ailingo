from unittest import mock
from unittest.mock import MagicMock

import pytest
from requests.exceptions import HTTPError

from ailingo.input_source.url_source import UrlInputSource


@pytest.mark.parametrize(
    "url, expected_path",
    [
        ("https://www.example.com", "https://www.example.com"),
        ("http://example.com", "http://example.com"),
    ],
)
def test_url_input_source_path(url: str, expected_path: str):
    url_input_source = UrlInputSource(url=url)
    assert url_input_source.path == expected_path


@pytest.mark.parametrize(
    "dryrun, expected_text",
    [
        (True, ""),
        (False, "test"),
    ],
)
def test_url_input_source_read(dryrun: bool, expected_text: str):
    url_input_source = UrlInputSource(url="https://www.example.com", dryrun=dryrun)
    with mock.patch("requests_html.HTMLSession.get") as mock_get:
        mock_response = MagicMock()
        mock_response.html.text = expected_text
        mock_get.return_value = mock_response
        text = url_input_source.read()
    assert text == expected_text


def test_url_input_source_read_http_error():
    url_input_source = UrlInputSource(url="https://www.example.com")
    with mock.patch("requests_html.HTMLSession.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = HTTPError
        mock_get.return_value = mock_response
        with pytest.raises(HTTPError):
            url_input_source.read()
