from utils.data_io import upload_to_gcs
from unittest.mock import patch


@patch("src.utils.data_io.storage.Client")
def test_upload_to_gcs(mock_client):
    mock_blob = mock_client.return_value.bucket.return_value.blob.return_value

    payload = {"foo": "bar"}
    upload_to_gcs("test-bucket", "path/file.json", payload)

    mock_blob.upload_from_string.assert_called_once()
