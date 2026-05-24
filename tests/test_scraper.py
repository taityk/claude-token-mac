"""Tests for scraper.py — all HTTP calls are mocked."""
import pytest
import requests

import scraper
from models import State


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ACCOUNT_RESPONSE = {
    "memberships": [
        {
            "organization": {
                "uuid": "test-org-uuid-1234"
            }
        }
    ]
}


def _make_usage_response(utilization: float) -> dict:
    return {
        "five_hour": {
            "utilization": utilization,
            "resets_at": "2026-05-24T18:00:01.162013+00:00",
        },
        "seven_day": {
            "utilization": 13.0,
            "resets_at": "2026-05-26T08:00:01.162036+00:00",
        },
        "seven_day_omelette": {
            "utilization": 100.0,
            "resets_at": "2026-05-26T08:00:01.162050+00:00",
        },
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_org_uuid_cache(mocker):
    """Reset the module-level _org_uuid cache between tests."""
    mocker.patch("scraper._org_uuid", None)
    yield
    # Ensure cache is cleared after each test too
    scraper._org_uuid = None


# ---------------------------------------------------------------------------
# _parse_response tests
# ---------------------------------------------------------------------------

class TestParseResponse:
    def test_normal_state(self):
        data = _make_usage_response(12.0)
        status = scraper._parse_response(data, warning_threshold=20)
        assert status.state == State.NORMAL
        assert status.remaining == 88
        assert status.reset_at is not None

    def test_warning_state(self):
        data = _make_usage_response(85.0)
        status = scraper._parse_response(data, warning_threshold=20)
        assert status.state == State.WARNING
        assert status.remaining == 15

    def test_warning_exactly_at_threshold(self):
        """remaining == warning_threshold should be WARNING."""
        data = _make_usage_response(80.0)  # remaining == 20
        status = scraper._parse_response(data, warning_threshold=20)
        assert status.state == State.WARNING
        assert status.remaining == 20

    def test_limited_state(self):
        data = _make_usage_response(100.0)
        status = scraper._parse_response(data, warning_threshold=20)
        assert status.state == State.LIMITED
        assert status.remaining == 0
        assert status.reset_at is not None

    def test_reset_at_is_datetime(self):
        from datetime import datetime, timezone
        data = _make_usage_response(12.0)
        status = scraper._parse_response(data, warning_threshold=20)
        assert isinstance(status.reset_at, datetime)
        # Should be timezone-aware
        assert status.reset_at.tzinfo is not None

    def test_fetched_at_is_set(self):
        from datetime import datetime
        data = _make_usage_response(50.0)
        status = scraper._parse_response(data, warning_threshold=20)
        assert isinstance(status.fetched_at, datetime)


# ---------------------------------------------------------------------------
# fetch_usage tests — mock _get_org_uuid and _get separately
# ---------------------------------------------------------------------------

class TestFetchUsage:
    def _mock_get(self, mocker, utilization: float):
        """Helper: mock _get_org_uuid and _get to return valid data."""
        mocker.patch("scraper._get_org_uuid", return_value="test-org-uuid-1234")

        mock_response = mocker.MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = _make_usage_response(utilization)
        mocker.patch("scraper._get", return_value=mock_response)

    def test_normal_state(self, mocker):
        self._mock_get(mocker, 12.0)
        status = scraper.fetch_usage("fake-cookie", warning_threshold=20)
        assert status.state == State.NORMAL
        assert status.remaining == 88

    def test_warning_state(self, mocker):
        self._mock_get(mocker, 85.0)
        status = scraper.fetch_usage("fake-cookie", warning_threshold=20)
        assert status.state == State.WARNING
        assert status.remaining == 15

    def test_limited_state(self, mocker):
        self._mock_get(mocker, 100.0)
        status = scraper.fetch_usage("fake-cookie", warning_threshold=20)
        assert status.state == State.LIMITED
        assert status.remaining == 0
        assert status.reset_at is not None

    def test_401_response_returns_unknown(self, mocker):
        mocker.patch("scraper._get_org_uuid", return_value="test-org-uuid-1234")

        mock_response = mocker.MagicMock()
        mock_response.ok = False
        mock_response.status_code = 401
        mocker.patch("scraper._get", return_value=mock_response)

        status = scraper.fetch_usage("bad-cookie", warning_threshold=20)
        assert status.state == State.UNKNOWN
        assert status.remaining is None

    def test_network_error_returns_unknown(self, mocker):
        mocker.patch("scraper._get_org_uuid", return_value="test-org-uuid-1234")
        mocker.patch("scraper._get", side_effect=requests.exceptions.ConnectionError("Network down"))

        status = scraper.fetch_usage("fake-cookie", warning_threshold=20)
        assert status.state == State.UNKNOWN

    def test_org_uuid_fetch_failure_returns_unknown(self, mocker):
        mocker.patch("scraper._get_org_uuid", return_value=None)

        status = scraper.fetch_usage("fake-cookie", warning_threshold=20)
        assert status.state == State.UNKNOWN

    def test_malformed_json_returns_unknown(self, mocker):
        mocker.patch("scraper._get_org_uuid", return_value="test-org-uuid-1234")

        mock_response = mocker.MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"unexpected": "structure"}
        mocker.patch("scraper._get", return_value=mock_response)

        status = scraper.fetch_usage("fake-cookie", warning_threshold=20)
        assert status.state == State.UNKNOWN


# ---------------------------------------------------------------------------
# _get_org_uuid tests
# ---------------------------------------------------------------------------

class TestGetOrgUuid:
    def test_fetches_and_caches(self, mocker):
        mock_resp = mocker.MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = ACCOUNT_RESPONSE

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_resp

        uuid = scraper._get_org_uuid(mock_session)
        assert uuid == "test-org-uuid-1234"
        assert scraper._org_uuid == "test-org-uuid-1234"

    def test_uses_cache_on_second_call(self, mocker):
        # Pre-populate the cache
        scraper._org_uuid = "cached-uuid"

        mock_session = mocker.MagicMock()

        uuid = scraper._get_org_uuid(mock_session)
        assert uuid == "cached-uuid"
        # Session.get should NOT have been called because we used the cache
        mock_session.get.assert_not_called()

    def test_returns_none_on_non_ok_response(self, mocker):
        mock_resp = mocker.MagicMock()
        mock_resp.ok = False

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_resp

        uuid = scraper._get_org_uuid(mock_session)
        assert uuid is None

    def test_returns_none_on_missing_memberships(self, mocker):
        mock_resp = mocker.MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {}

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_resp

        uuid = scraper._get_org_uuid(mock_session)
        assert uuid is None

    def test_returns_none_on_empty_memberships(self, mocker):
        mock_resp = mocker.MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"memberships": []}

        mock_session = mocker.MagicMock()
        mock_session.get.return_value = mock_resp

        uuid = scraper._get_org_uuid(mock_session)
        assert uuid is None
