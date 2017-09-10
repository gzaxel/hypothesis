# coding=utf-8
#
# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis-python
#
# Most of this work is copyright (C) 2013-2017 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.
#
# END HEADER

from __future__ import division, print_function, absolute_import

import time
import warnings

import pytest

import hypothesis.strategies as st
from hypothesis import given, settings
from hypothesis.errors import DeadlineExceeded, \
    HypothesisDeprecationWarning
from tests.common.utils import checks_deprecated_behaviour


def test_raises_deadline_on_slow_test():
    @settings(deadline=500)
    @given(st.integers())
    def slow(i):
        time.sleep(1)

    with pytest.raises(DeadlineExceeded):
        slow()


def test_only_warns_once():
    @given(st.integers())
    def slow(i):
        time.sleep(1)
    try:
        warnings.simplefilter('always', HypothesisDeprecationWarning)
        with warnings.catch_warnings(record=True) as w:
            slow()
    finally:
        warnings.simplefilter('error', HypothesisDeprecationWarning)
    assert len(w) == 1


@checks_deprecated_behaviour
@given(st.integers())
def test_slow_tests_are_deprecated_by_default(i):
    time.sleep(1)


@given(st.integers())
@settings(deadline=None)
def test_slow_with_none_deadline(i):
    time.sleep(1)
