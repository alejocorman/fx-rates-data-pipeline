from utils.data_io import blob_exists
from unittest.mock import patch


@patch("utils.data_io.storage.Client")
def test_blob_exists_true(mock_client):
    mock_blob = mock_client.return_value.bucket.return_value.blob.return_value
    mock_blob.exists.return_value = True

    assert blob_exists("test-bucket", "path/file.json") is True
