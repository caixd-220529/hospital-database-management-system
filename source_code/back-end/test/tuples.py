from collections.abc import Iterable
from fields import *

"""
class used to generate tuples for database testing
"""


class TupleGenerator:
    def __init__(self, *args):
        """
        :param args: Fields in a tuple, each arg should be a Field or a collections of Fields
        """

        self.fields = []
        for arg in args:
            if isinstance(arg, Iterable):
                self.fields += [x for x in arg if isinstance(x, Field)]
            elif isinstance(arg, Field):
                self.fields.append(arg)

    def generate_random_tuple(self):
        """ Generate a random tuple """
        return tuple([field.random_data_generator() for field in self.fields])

    def generate_random_tuples(self, n):
        """ Generate n random tuples """
        return [self.generate_random_tuple() for _ in range(n)]


# use cases:
# Name = StringField(length_range=(2, 10))
# Age = IntField(value_range=(0, 100))
# Birth = DatetimeField()
# Salary = IntField(value_range=(100, 100000))
#
# tg = TupleGenerator(Name, Age, Birth, Salary)
# print(tg.generate_random_tuples(10))
