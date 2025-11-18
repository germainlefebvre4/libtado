from datetime import datetime, timezone, timedelta

from libtado.api import RateLimitInfo

class TestRateLimitInfo:
    def test_no_headers(self):
        info = RateLimitInfo(None, None)
        assert info.granted_calls is None
        assert info.granted_calls_period_in_seconds is None
        assert info.remaining_calls is None
        assert info.ratelimit_resets_at_utc is None

    def test_garbage_headers(self):
        info = RateLimitInfo('Grrr', 'Hmm')
        assert info.granted_calls is None
        assert info.granted_calls_period_in_seconds is None
        assert info.remaining_calls is None
        assert info.ratelimit_resets_at_utc is None

        info = RateLimitInfo('"perday"', '"perday";r')
        assert info.granted_calls is None
        assert info.granted_calls_period_in_seconds is None
        assert info.remaining_calls is None
        assert info.ratelimit_resets_at_utc is None

    def test_valid_headers(self):
        info_with_t = RateLimitInfo('"perday";q=20000;w=86400', '"perday";r=15500;t=123')
        assert info_with_t.granted_calls == 20000
        assert info_with_t.granted_calls_period_in_seconds == 86400
        assert info_with_t.remaining_calls == 15500
        # compare only up to the minute, to avoid errors due to small time differene while running the test.
        assert info_with_t.ratelimit_resets_at_utc.strftime("%m/%d/%Y, %H:%M") == (datetime.now(timezone.utc) + timedelta(seconds=123)).strftime("%m/%d/%Y, %H:%M")

        info_without_t = RateLimitInfo('"perday";q=160000;w=604800', '"perday";r=14000')
        assert info_without_t.granted_calls == 160000
        assert info_without_t.granted_calls_period_in_seconds == 604800
        assert info_without_t.remaining_calls == 14000
        assert info_without_t.ratelimit_resets_at_utc is None

        info_exhausted = RateLimitInfo('"perday";q=100;w=86400', '"perday";r=0;t=240')
        assert info_exhausted.granted_calls == 100
        assert info_exhausted.granted_calls_period_in_seconds == 86400
        assert info_exhausted.remaining_calls == 0
        assert info_exhausted.ratelimit_resets_at_utc.strftime("%m/%d/%Y, %H:%M") == (datetime.now(timezone.utc) + timedelta(seconds=240)).strftime("%m/%d/%Y, %H:%M")
