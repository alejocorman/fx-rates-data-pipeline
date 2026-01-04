import os
import logging
from datetime import date
from utils.data_io import fetch_rates, upload_to_gcs, blob_exists

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ---------- Config ----------
BUCKET_NAME = os.getenv("GCS_BUCKET")
if not BUCKET_NAME:
    raise ValueError("GCS_BUCKET environment variable is not set")

SOURCE_NAME = "frankfurter"
BASE_CURRENCY = "USD"
TARGET_CURRENCIES = ["EUR", "GBP", "JPY"]

# ---------- Execution date ----------
execution_date = date.today().isoformat()

logger.info(
    "Starting ingestion",
    extra={
        "source": SOURCE_NAME,
        "execution_date": execution_date,
        "base": BASE_CURRENCY,
        "targets": TARGET_CURRENCIES,
    },
)

# ---------- Fetch data ----------
api_url = "https://api.frankfurter.dev/v1/latest"
params = {
    "base": BASE_CURRENCY,
    "symbols": ",".join(TARGET_CURRENCIES),
}

payload = fetch_rates(api_url, params)

data_date = payload.get("date")
if not data_date:
    raise ValueError("API payload does not contain 'date' field")

blob_path = f"raw/api={SOURCE_NAME}/date={data_date}.json"

# ---------- Data freshness check (non-blocking) ----------
if data_date != execution_date:
    logger.info(
        "API returned stale data",
        extra={
            "data_date": data_date,
            "execution_date": execution_date,
        },
    )

# ---------- Idempotency check ----------
if blob_exists(BUCKET_NAME, blob_path):
    logger.warning(
        "Raw data already exists for data date. Skipping ingestion.",
        extra={"blob_path": blob_path},
    )
else:
    upload_to_gcs(BUCKET_NAME, blob_path, payload)
    logger.info(
        "Raw data uploaded successfully",
        extra={"blob_path": blob_path},
    )

logger.info("Ingestion finished successfully")
