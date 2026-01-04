from utils.data_io import fetch_rates
import requests_mock


def test_fetch_rates_success():
    api_url = "https://fake.api"
    params = {"base": "USD"}

    mock_response = {"base": "USD", "rates": {"EUR": 0.9}}

    with requests_mock.Mocker() as m:
        m.get(api_url, json=mock_response, status_code=200)
        result = fetch_rates(api_url, params)

    assert result["base"] == "USD"
    assert "rates" in result
