import string
import sys
from collections.abc import Iterable, Sized
import re
import random

MAX_STRING_LENGTH = 1 << 31
MAX_DATE_NUMBER = 1 << 31

"""

Classes for generating fields for database table, each class (expect base) implements random_data_generator()
method to generate random test data. Restrictions on data can be constructed on initialization, see details on each
class's __init__ method

You can specify a null rate by passing key-word argument null_rate to generate None value, representing NULL value in 
database. null_rate must be in [0.0, 1.0], default value is 0.0

"""


class Field:

    def __init__(self, field_type: str = 'int', default_value=None, null_rate: float = 0.0):
        """
        :param field_type: type of field
        :param default_value: default value of field
        :param null_rate: chance that a random data generator generates None, NOT NULL if set to 0.0, value must be in [0.0, 1.0]
        """
        self.field_type = field_type
        self.default_value = default_value

        assert 0.0 <= null_rate <= 1.0, 'Invalid null rate!'
        self.null_rate = null_rate

    def random_data_generator(self):
        pass

    def static_data_generator(self, value):
        pass

    @staticmethod
    def get_range_from_iterable(iterable, dtype: type):
        assert len(iterable) == 2, 'Invalid RealField range value!'
        begin, end = iterable
        assert isinstance(begin, dtype) and isinstance(end, dtype) and begin <= end, 'Invalid RealField range value!'
        return tuple(iterable)

    @staticmethod
    def get_range_from_string(string: str, dtype: type) -> tuple:
        """
        Use re to match all dtype data (INTEGER, FLOAT).
        :param string: string that contains range information
        :param dtype: data type (int, float)
        :return: tuple range indicated in the string
        """
        if dtype == int:
            pattern = re.compile(r'\d+')
        else:
            pattern = re.compile(r'\d+\.\d+')
        nums = pattern.findall(string)
        assert len(nums) == 2 and nums[0] <= nums[1], 'Invalid IntField range value!'
        return tuple(map(dtype, nums))

    @staticmethod
    def get_range_from_anywhere(value_range, dtype: type):
        if isinstance(value_range, str):
            return Field.get_range_from_string(value_range, dtype)
        elif isinstance(value_range, Iterable) and isinstance(value_range, Sized):
            return Field.get_range_from_iterable(value_range, dtype)
        else:
            raise ValueError('Unrecognized Field range value!')


class IntField(Field):

    def __init__(self, value_range=(0, 1), default_value: int = 0, **kwargs):
        """
        IntField initializer

        :param value_range: range of generated integer, can be a container with 2 integer elements, or any string that conatins 2 integers
        :param default_value: default integer value
        """

        super().__init__('int', default_value=default_value, **kwargs)
        self.value_range = IntField.get_range_from_anywhere(value_range, int)

    def random_data_generator(self):
        """
        Generate random integer in the range.
        :return: a random int or None
        """
        return random.choices([random.randint(*self.value_range), None],
                              weights=[1-self.null_rate, self.null_rate], k=1)[0]


class StringField(Field):

    def __init__(self, length_range=(-1, -1), default_value: str = None, dictionary: Iterable = None, use_ascii=True, **kwargs):
        """
        StringField initializer

        :param length_range: range limit on length of generated strings
        :param default_value: default string, if not provided, is a string of space with length of length_range[0]
        :param dictionary: a collections of words that will be randomly picked by generator, if provided
        """
        length_range = StringField.get_range_from_anywhere(length_range, int)
        if length_range[0] < 0:
            length_range = (0, length_range[1])
        if length_range[1] < 0:
            length_range = (0, MAX_STRING_LENGTH)
        if default_value is not None:
            assert length_range[0] <= len(default_value) <= length_range[1], 'Invalid StringField default value'
        else:
            default_value = f"{' ' * length_range[0]}"

        super().__init__('string', default_value=default_value, **kwargs)

        self.dictionary = None
        if dictionary is not None:
            self.dictionary = list(dictionary)

        if use_ascii:
            self.characters = string.ascii_letters
        else:
            self.characters = [chr(i) for i in range(0, sys.maxunicode) if chr(i).isprintable()]
        self.length_range = length_range

    def random_data_generator(self):
        """
        Generate random string.
        If a dictionary is provided, randomly choose a string from the dictionary, and slice the string by range.
        If not, randomly generate a string from unicode characters with random length.
        :return: a random string or None
        """
        if self.dictionary is not None:
            random_string = random.choice(self.dictionary)[0:self.length_range[1]-self.length_range[0]]
            return random.choices([random_string, None], weights=[1-self.null_rate, self.null_rate], k=1)[0]

        else:
            if random.choices([True, False], weights=[self.null_rate, 1-self.null_rate], k=1)[0]:
                return None
            random_string = ''
            for _ in range(random.randint(*self.length_range)):
                random_string += random.choice(self.characters)
            return random_string


class RealField(Field):

    def __init__(self, value_range=(0, 1), default_value: float = 0.0, **kwargs):
        """
        RealField initializer

        :param value_range: range of real value generated, can be a container of 2 elements or any string that contains 2 numbers
        :param default_value: default real value
        """
        super().__init__('real', default_value=default_value, **kwargs)

        self.value_range = RealField.get_range_from_anywhere(value_range, float)

    def random_data_generator(self):
        """
        Generate random float in the range.
        :return: a random float or None
        """
        return random.choices([random.uniform(*self.value_range), None],
                              weights=[1-self.null_rate, self.null_rate], k=1)[0]


class DatetimeField(Field):

    def __init__(self,
                 default_value: str = '1970-01-01 00:00:00',
                 allow_invalid: bool = False,
                 check_day: bool = True,
                 force_format: str = '{y}-{m}-{d} {H}:{M}:{S}',
                 range_dict: dict = None, **kwargs):
        """
        DatetimeField initializer

        :param default_value: default value of the field
        :param allow_invalid: whether invalid datetime is allowed or not
        :param check_day: whether check if the day is valid within a month
        :param force_format: y, m, d, H, M, S stands for year, month, day, hour, minute, second, should be in braces
        :param range_dict: dict for ranges of date component, see default layout below
        """

        super().__init__('datetime', default_value=default_value, **kwargs)

        self.check_day = check_day
        self.allow_invalid = allow_invalid
        self.force_format = force_format

        # { 'date column -> (range)' }
        self.range_dict = {'year': (0, 9999),
                           'month': (1, 12),
                           'day': (1, 31),
                           'hour': (0, 23),
                           'minute': (0, 59),
                           'second': (0, 59)}

        if range_dict is not None:
            for key, value in range_dict.items():
                assert isinstance(key, str), 'Invalid DatetimeField range dictionary key!'

                if key.lower() in ['y', 'yyyy', 'year']:
                    self.range_dict['year'] = DatetimeField.get_range_from_anywhere(value, int)
                elif key.lower() in ['m', 'mm', 'month']:
                    self.range_dict['month'] = DatetimeField.get_range_from_anywhere(value, int)
                elif key.lower() in ['d', 'dd', 'day']:
                    self.range_dict['day'] = DatetimeField.get_range_from_anywhere(value, int)
                elif key.lower() in ['h', 'hh', 'hour']:
                    self.range_dict['hour'] = DatetimeField.get_range_from_anywhere(value, int)
                elif key.lower() in ['min', 'minute']:
                    self.range_dict['minute'] = DatetimeField.get_range_from_anywhere(value, int)
                elif key.lower() in ['s', 'ss', 'second']:
                    self.range_dict['second'] = DatetimeField.get_range_from_anywhere(value, int)

    def gen_datetime_column(self, column: str, year=None, month=None):
        if self.allow_invalid:
            return random.randint(-MAX_DATE_NUMBER, MAX_DATE_NUMBER)
        else:
            if self.check_day and year is not None and month is not None:
                assert column == 'day'
                max_day = 31
                if month == 2:
                    max_day = 28 + (year % 4 == 0 and year % 100 != 0)
                elif month in {2, 4, 6, 9, 11}:
                    max_day = 30
                begin, end = self.range_dict[column]
                end = min(end, max_day)
                return random.randint(begin, end)
            return random.randint(*self.range_dict[column])

    def random_data_generator(self):
        """
        Generate random datetime.
        :return: a random datetime (str) or None
        """

        year = '{:>04}'.format(self.gen_datetime_column('year'))
        month = '{:>02}'.format(self.gen_datetime_column('month'))
        day = '{:>02}'.format(self.gen_datetime_column('day', year, month))
        hour = '{:>02}'.format(self.gen_datetime_column('hour'))
        minute = '{:>02}'.format(self.gen_datetime_column('minute'))
        second = '{:>02}'.format(self.gen_datetime_column('second'))

        random_datetime = self.force_format.format(y=year, m=month, d=day, H=hour, M=minute, S=second)
        return random.choices([random_datetime, None], weights=[1 - self.null_rate, self.null_rate], k=1)[0]


# Use cases:
# intField = IntField(value_range='0 to 100')
#
# words = ['apple', 'pear', 'peach']
# stringField1 = StringField(length_range='2, 10', dictionary=words)
#
# stringField2 = StringField(length_range=(2, 10), use_ascii=True)
#
# datetimeField = DatetimeField()
#
# for _ in range(10000):
#     print(stringField2.random_data_generator())
# print('\u0001')

