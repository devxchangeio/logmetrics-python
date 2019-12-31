import sys
import time


if sys.platform == 'win32':
    try:  # Python 3.4+
        preferred_clock = time.perf_counter
    except AttributeError:  # Earlier than Python 3.
        preferred_clock = time.clock
else:
    preferred_clock = time.time


class TimeUtil:
    """
    Static class for performing Rounding and Time-related Calculation for code execution
    """
    _time_multiplier = 1_000
    _time_ndigits = 0
    _time_func = int

    @classmethod
    def set_internal_state(cls, time_units='ms', time_ndigits=0, round_to_closest_int=False):
        if time_units == 'ms':
            cls._time_multiplier = 1_000
            cls._time_ndigits = time_ndigits
        elif time_units == 's':
            cls._time_multiplier = 1
            cls._time_ndigits = time_ndigits or 3
        else:
            raise ValueError('Units of time must be one of [s, ms].')

        cls._time_func = round if cls._time_ndigits or round_to_closest_int else int

    @classmethod
    def get_duration(cls, start, end):
        """
        Assuming that `start` and `end` are values in seconds, calculate the result as the
        time difference between the two values.

        The result is expressed with the units and precision of the class's internal state.

        Returns
        -------
        duration : int or float
            Returns float value if `time_ndigits` is non-zero, otherwise an int value.

        """
        duration = (end - start) * cls._time_multiplier
        return cls._time_func(duration, cls._time_ndigits) if cls._time_ndigits else cls._time_func(duration)

    @classmethod
    def round_if_needed(cls, o):
        """
        If the value `o` is determined to be a float, it is rounded with the precision
        contained in the class's internal state. Otherwise, the value itself is returned.

        This method relies on the assumption that if `time_ndigits` is 0,
        then the parameter `o` must be an ``int``.

        The main use-case for floating-point rounding is due to
        floating-point arithmetic and its limitations (such as representation issues).\
        Reference: https://docs.python.org/3/tutorial/floatingpoint.html

        Returns
        -------
        rounded_number : int or float
            Returns float value if `time_ndigits` is non-zero, otherwise an int value.

        """
        return cls._time_func(o, cls._time_ndigits) if cls._time_ndigits else o

