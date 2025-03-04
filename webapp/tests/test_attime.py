from mock import patch
import datetime
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from django.test import TestCase
from django.utils import timezone
from graphite.render.attime import parseTimeReference, parseATTime, parseTimeOffset, getUnitString

MOCK_DATE = datetime.datetime(2015, 1, 1, 11, 00)


class parseTimeTest(TestCase):

    def setUp(self):
        self.patcher = patch.object(timezone, 'now', return_value=MOCK_DATE)
        self.mock_now = self.patcher.start()

    def tearDown(self):
        self.patcher.stop()


class parseTimeReferenceTest(parseTimeTest):

    def test_parse_empty_return_now(self):
        time_ref = parseTimeReference('')
        self.assertEquals(time_ref, MOCK_DATE)

    def test_parse_None_return_now(self):
        time_ref = parseTimeReference(None)
        self.assertEquals(time_ref, MOCK_DATE)

    def test_parse_random_string_raise_Exception(self):
        with self.assertRaises(Exception):
            time_ref = parseTimeReference("random")

    def test_parse_now_return_now(self):
        time_ref = parseTimeReference("now")
        self.assertEquals(time_ref, MOCK_DATE)

    def test_parse_colon_raises_ValueError(self):
        with self.assertRaises(ValueError):
            time_ref = parseTimeReference(":")

    def test_parse_hour_return_hour_of_today(self):
        time_ref = parseTimeReference("8:50")
        expected = datetime.datetime(MOCK_DATE.year, MOCK_DATE.month, MOCK_DATE.day, 8, 50)
        self.assertEquals(time_ref, expected)

    def test_parse_hour_am(self):
        time_ref = parseTimeReference("8:50am")
        expected = datetime.datetime(MOCK_DATE.year, MOCK_DATE.month, MOCK_DATE.day, 8, 50)
        self.assertEquals(time_ref, expected)

    def test_parse_hour_pm(self):
        time_ref = parseTimeReference("8:50pm")
        expected = datetime.datetime(MOCK_DATE.year, MOCK_DATE.month, MOCK_DATE.day, 20, 50)
        self.assertEquals(time_ref, expected)

    def test_parse_noon(self):
        time_ref = parseTimeReference("noon")
        expected = datetime.datetime(MOCK_DATE.year, MOCK_DATE.month, MOCK_DATE.day, 12, 0)
        self.assertEquals(time_ref, expected)

    def test_parse_midnight(self):
        time_ref = parseTimeReference("midnight")
        expected = datetime.datetime(MOCK_DATE.year, MOCK_DATE.month, MOCK_DATE.day, 0, 0)
        self.assertEquals(time_ref, expected)

    def test_parse_teatime(self):
        time_ref = parseTimeReference("teatime")
        expected = datetime.datetime(MOCK_DATE.year, MOCK_DATE.month, MOCK_DATE.day, 16, 0)
        self.assertEquals(time_ref, expected)

    def test_parse_yesterday(self):
        time_ref = parseTimeReference("yesterday")
        expected = datetime.datetime(2014, 12, 31, 0, 0)
        self.assertEquals(time_ref, expected)

    def test_parse_tomorrow(self):
        time_ref = parseTimeReference("tomorrow")
        expected = datetime.datetime(2015, 1, 2, 0, 0)
        self.assertEquals(time_ref, expected)

    def test_parse_MM_slash_DD_slash_YY(self):
        time_ref = parseTimeReference("02/25/15")
        expected = datetime.datetime(2015, 2, 25, 0, 0)
        self.assertEquals(time_ref, expected)

    def test_parse_MM_slash_DD_slash_YYYY(self):
        time_ref = parseTimeReference("02/25/2015")
        expected = datetime.datetime(2015, 2, 25, 0, 0)
        self.assertEquals(time_ref, expected)

    def test_parse_YYYYMMDD(self):
        time_ref = parseTimeReference("20140606")
        expected = datetime.datetime(2014, 6, 6, 0, 0)
        self.assertEquals(time_ref, expected)

    def test_parse_MonthName_DayOfMonth_onedigits(self):
        time_ref = parseTimeReference("january8")
        expected = datetime.datetime(2015, 1, 8, 0, 0)
        self.assertEquals(time_ref, expected)

    def test_parse_MonthName_DayOfMonth_twodigits(self):
        time_ref = parseTimeReference("january10")
        expected = datetime.datetime(2015, 1, 10, 0, 0)
        self.assertEquals(time_ref, expected)

    def test_parse_MonthName_DayOfMonth_threedigits_raise_ValueError(self):
        with self.assertRaises(ValueError):
            time_ref = parseTimeReference("january800")

    def test_parse_MonthName_without_DayOfMonth_raise_Exception(self):
        with self.assertRaises(Exception):
            time_ref = parseTimeReference("january")

    def test_parse_monday_return_monday_before_now(self):
        time_ref = parseTimeReference("monday")
        expected = datetime.datetime(2014, 12, 29, 0, 0)
        self.assertEquals(time_ref, expected)


class parseTimeOffsetTest(TestCase):

    def test_parse_None_returns_empty_timedelta(self):
        time_ref = parseTimeOffset(None)
        expected = datetime.timedelta(0)
        self.assertEquals(time_ref, expected)

    def test_parse_integer_raises_TypeError(self):
        with self.assertRaises(TypeError):
            time_ref = parseTimeOffset(1)

    def test_parse_string_starting_neither_with_minus_nor_digit_raises_KeyError(self):
        with self.assertRaises(KeyError):
            time_ref = parseTimeOffset("Something")

    def test_parse_m_as_unit_raises_Exception(self):
        with self.assertRaises(Exception):
            time_ref = parseTimeOffset("1m")

    def test_parse_digits_only_raises_exception(self):
        with self.assertRaises(Exception):
            time_ref = parseTimeOffset("10")

    def test_parse_alpha_only_raises_KeyError(self):
        with self.assertRaises(KeyError):
            time_ref = parseTimeOffset("month")

    def test_parse_minus_only_returns_zero(self):
        time_ref = parseTimeOffset("-")
        expected = datetime.timedelta(0)
        self.assertEquals(time_ref, expected)

    def test_parse_plus_only_returns_zero(self):
        time_ref = parseTimeOffset("+")
        expected = datetime.timedelta(0)
        self.assertEquals(time_ref, expected)

    def test_parse_ten_days(self):
        time_ref = parseTimeOffset("10days")
        expected = datetime.timedelta(10)
        self.assertEquals(time_ref, expected)

    def test_parse_zero_days(self):
        time_ref = parseTimeOffset("0days")
        expected = datetime.timedelta(0)
        self.assertEquals(time_ref, expected)

    def test_parse_minus_ten_days(self):
        time_ref = parseTimeOffset("-10days")
        expected = datetime.timedelta(-10)
        self.assertEquals(time_ref, expected)

    def test_parse_five_seconds(self):
        time_ref = parseTimeOffset("5seconds")
        expected = datetime.timedelta(seconds=5)
        self.assertEquals(time_ref, expected)

    def test_parse_five_minutes(self):
        time_ref = parseTimeOffset("5minutes")
        expected = datetime.timedelta(minutes=5)
        self.assertEquals(time_ref, expected)

    def test_parse_five_hours(self):
        time_ref = parseTimeOffset("5hours")
        expected = datetime.timedelta(hours=5)
        self.assertEquals(time_ref, expected)

    def test_parse_five_weeks(self):
        time_ref = parseTimeOffset("5weeks")
        expected = datetime.timedelta(weeks=5)
        self.assertEquals(time_ref, expected)

    def test_parse_one_month_returns_thirty_days(self):
        time_ref = parseTimeOffset("1month")
        expected = datetime.timedelta(30)
        self.assertEquals(time_ref, expected)

    def test_parse_two_months_returns_sixty_days(self):
        time_ref = parseTimeOffset("2months")
        expected = datetime.timedelta(60)
        self.assertEquals(time_ref, expected)

    def test_parse_twelve_months_returns_360_days(self):
        time_ref = parseTimeOffset("12months")
        expected = datetime.timedelta(360)
        self.assertEquals(time_ref, expected)

    def test_parse_one_year_returns_365_days(self):
        time_ref = parseTimeOffset("1year")
        expected = datetime.timedelta(365)
        self.assertEquals(time_ref, expected)

    def test_parse_two_years_returns_730_days(self):
        time_ref = parseTimeOffset("2years")
        expected = datetime.timedelta(730)
        self.assertEquals(time_ref, expected)


class getUnitStringTest(TestCase):

    def test_get_seconds(self):
        test_cases = ['s', 'se', 'sec', 'second', 'seconds']
        for test_case in test_cases:
            result = getUnitString(test_case)
            self.assertEquals(result, 'seconds')

    def test_get_minutes(self):
        test_cases = ['min', 'minute', 'minutes']
        for test_case in test_cases:
            result = getUnitString(test_case)
            self.assertEquals(result, 'minutes')

    def test_get_hours(self):
        test_cases = ['h', 'ho', 'hour', 'hours']
        for test_case in test_cases:
            result = getUnitString(test_case)
            self.assertEquals(result, 'hours')

    def test_get_days(self):
        test_cases = ['d', 'da', 'day', 'days']
        for test_case in test_cases:
            result = getUnitString(test_case)
            self.assertEquals(result, 'days')

    def test_get_weeks(self):
        test_cases = ['w', 'we', 'week', 'weeks']
        for test_case in test_cases:
            result = getUnitString(test_case)
            self.assertEquals(result, 'weeks')

    def test_get_months(self):
        test_cases = ['mon', 'month', 'months']
        for test_case in test_cases:
            result = getUnitString(test_case)
            self.assertEquals(result, 'months')

    def test_get_years(self):
        test_cases = ['y', 'ye', 'year', 'years']
        for test_case in test_cases:
            result = getUnitString(test_case)
            self.assertEquals(result, 'years')

    def test_m_raises_Exception(self):
        with self.assertRaises(Exception):
            result = getUnitString("m")

    def test_integer_raises_Exception(self):
        with self.assertRaises(Exception):
            result = getUnitString(1)


class parseATTimeTest(parseTimeTest):

    @unittest.expectedFailure
    def test_parse_noon_plus_yesterday(self):
        time_ref = parseATTime("noon+yesterday")
        expected = datetime.datetime(MOCK_DATE.year, MOCK_DATE.month, MOCK_DATE.day - 1, 12, 00)
        self.assertEquals(time_ref, expected)
