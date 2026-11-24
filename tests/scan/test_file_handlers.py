import os

from unittest.mock import Mock, patch
from safety.scan.finder.handlers import PythonFileHandler


@patch("safety.safety.fetch_database")
def test_download_required_assets(mock_fetch_database):
    handler = PythonFileHandler()
    session = Mock()

    with patch.dict(os.environ, {"SAFETY_DB_DIR": "/path/to/db"}):
        handler.download_required_assets(session)

    _, kwargs = mock_fetch_database.call_args

    assert kwargs["db"] == "/path/to/db"


@patch("safety.safety.fetch_database")
def test_download_required_assets_no_db_dir(mock_fetch_database):
    handler = PythonFileHandler()
    session = Mock()

    with patch.dict(os.environ, {}, clear=True):
        handler.download_required_assets(session)

    _, kwargs = mock_fetch_database.call_args

    assert not kwargs["db"]


@patch("safety.safety.fetch_database")
def test_download_required_assets_passes_private_index(mock_fetch_database):
    handler = PythonFileHandler()
    session = Mock()

    with patch.dict(os.environ, {}, clear=True):
        handler.download_required_assets(
            session,
            index_url="https://packages.example.test/safety",
            offline=True,
        )

    _, kwargs = mock_fetch_database.call_args
    assert kwargs["index_url"] == "https://packages.example.test/safety"
    assert kwargs["offline"] is True
