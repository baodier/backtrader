#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015-2023 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from copy import copy


class PositionA(object):
    '''
    Keeps and updates the size and price of a position. The object has no
    relationship to any asset. It only keeps size and price.

    Member Attributes:
      - size (int): current size of the position
      - price (float): current price of the position

    The Position instances can be tested using len(position) to see if size
    is not null
    '''

    def __str__(self):
        items = list()
        # items.append('--- PositionA Begin')
        items.append(' Size: {}'.format(self.size))
        items.append(' HoldSize: {}'.format(self.holdsize))
        items.append(' HoldDate: {}'.format(self.holddate))
        items.append(' Price: {}'.format(self.price))
        items.append(' Price orig: {}'.format(self.price_orig))
        items.append(' Closed: {}'.format(self.upclosed))
        items.append(' Opened: {}'.format(self.upopened))
        items.append(' Adjbase: {}'.format(self.adjbase))
        # items.append('--- Position End')
        # return '\n'.join(items)
        return ''.join(items)
    def __init__(self, size=0, price=0.0, holdsize=0, holddate=None):
        self.size = size
        self.holdsize = holdsize
        self.holddate = holddate
        if size:
            self.price = self.price_orig = price
        else:
            self.price = 0.0

        self.adjbase = None

        self.upopened = size
        self.upclosed = 0
        # self.set(size, price)
        self.price_orig = self.price

        self.updt = None

    # def fix(self, size, price):
    #     oldsize = self.size
    #     self.size = size
    #     self.price = price
    #     return self.size == oldsize
    #
    # def set(self, size, price):
    #     if self.size > 0:
    #         if size > self.size:
    #             self.upopened = size - self.size  # new 10 - old 5 -> 5
    #             self.upclosed = 0
    #         else:
    #             # same side min(0, 3) -> 0 / reversal min(0, -3) -> -3
    #             self.upopened = min(0, size)
    #             # same side min(10, 10 - 5) -> 5
    #             # reversal min(10, 10 - -5) -> min(10, 15) -> 10
    #             self.upclosed = min(self.size, self.size - size)
    #
    #     elif self.size < 0:
    #         if size < self.size:
    #             self.upopened = size - self.size  # ex: -5 - -3 -> -2
    #             self.upclosed = 0
    #         else:
    #             # same side max(0, -5) -> 0 / reversal max(0, 5) -> 5
    #             self.upopened = max(0, size)
    #             # same side max(-10, -10 - -5) -> max(-10, -5) -> -5
    #             # reversal max(-10, -10 - 5) -> max(-10, -15) -> -10
    #             self.upclosed = max(self.size, self.size - size)
    #
    #     else:  # self.size == 0
    #         self.upopened = self.size
    #         self.upclosed = 0
    #
    #     self.size = size
    #     self.price_orig = self.price
    #     if size:
    #         self.price = price
    #     else:
    #         self.price = 0.0
    #
    #     return self.size, self.price, self.upopened, self.upclosed

    def __len__(self):
        return abs(self.size)

    def __bool__(self):
        return bool(self.size != 0)

    __nonzero__ = __bool__

    def clone(self):
        return PositionA(size=self.size, price=self.price, holdsize=self.holdsize, holddate=self.holddate)

    def pseudoupdate(self, size, price, dt):
        return PositionA(self.size, self.price, self.holdsize, self.holddate).update(size, price, dt)

    def update(self, size, price, dt):
        self.datetime = dt  # record datetime update (datetime.datetime)

        self.price_orig = self.price
        oldsize = self.size
        # self.size += size

        if size >= 0:
            opened, closed = size, 0
            self.size += size
            self.price = (self.price * oldsize + size * price) / self.size
            # 如果是买入的，需要修改holdsize和holddate
            if self.holddate is None:
                self.holddate = dt.date()
                self.holdsize = size
            else:
                assert self.holddate <= dt.date(), "holddate {} cannot be larger than execute date {}".format(self.holddate, dt.date())
                if self.holddate == dt.date():
                    self.holdsize += size
                else:
                    self.holddate = dt.date()
                    self.holdsize = size
        else:
            if self.holddate is None:
                activesize = oldsize
            else:
                activesize = oldsize if dt.date() > self.holddate else oldsize - self.holdsize
            # self.price = self.price
            if activesize + size >= 0:
                opened, closed = 0, size
                self.size += size
            else:
                opened, closed = 0, 0
                print('cannot sell, not enough amounts, size={}, raw_size={}, holdsize={}, usefulsize={}, '
                      'holddate={}, thisday={}'.format(size, self.size, self.holdsize, self.size - self.holdsize,
                                                       self.holddate, self.datetime))

        self.upopened = opened
        self.upclosed = closed

        return self.size, self.price, opened, closed
