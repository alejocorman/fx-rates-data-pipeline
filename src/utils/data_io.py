import json
import logging
import requests
from google.cloud import storage

logger = logging.getLogger(__name__)


def fetch_rates(api_url: str, params: dict) -> dict:
    logger.info("Fetching data from API", extra={"url": api_url, "params": params})

    try:
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()

    except requests.RequestException as exc:
        logger.error(
            "Error fetching data from API",
            extra={"url": api_url, "params": params},
        )
        raise exc

    return response.json()


def blob_exists(bucket_name: str, blob_path: str) -> bool:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    return bucket.blob(blob_path).exists()


def upload_to_gcs(bucket_name: str, blob_path: str, payload: dict) -> None:
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    blob.upload_from_string(
        json.dumps(payload, ensure_ascii=False),
        content_type="application/json",
    )

    logger.info(
        "Data uploaded to GCS",
        extra={"bucket": bucket_name, "blob_path": blob_path},
    )
