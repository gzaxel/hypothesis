# This file is part of Hypothesis, which may be found at
# https://github.com/HypothesisWorks/hypothesis/
#
# Most of this work is copyright (C) 2013-2021 David R. MacIver
# (david@drmaciver.com), but it contains contributions by others. See
# CONTRIBUTING.rst for a full list of people who may hold copyright, and
# consult the git log if you need to determine who owns an individual
# contribution.
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at https://mozilla.org/MPL/2.0/.
#
# END HEADER

import pytest

from hypothesis import Phase, example, given, settings, strategies as st
from hypothesis.database import ExampleDatabase, InMemoryExampleDatabase
from hypothesis.errors import InvalidArgument


@example(11)
@settings(phases=(Phase.explicit,))
@given(st.integers())
def test_only_runs_explicit_examples(i):
    assert i == 11


@example("hello world")
@settings(phases=(Phase.reuse, Phase.generate, Phase.shrink))
@given(st.booleans())
def test_does_not_use_explicit_examples(i):
    assert isinstance(i, bool)


@settings(phases=(Phase.reuse, Phase.shrink))
@given(st.booleans())
def test_this_would_fail_if_you_ran_it(b):
    raise AssertionError


@pytest.mark.parametrize(
    "arg,expected",
    [
        (tuple(Phase)[::-1], tuple(Phase)),
        ([Phase.explicit, Phase.explicit], (Phase.explicit,)),
    ],
)
def test_sorts_and_dedupes_phases(arg, expected):
    assert settings(phases=arg).phases == expected


def test_phases_default_to_all_except_explain():
    assert settings().phases + (Phase.explain,) == tuple(Phase)


def test_does_not_reuse_saved_examples_if_reuse_not_in_phases():
    class BadDatabase(ExampleDatabase):
        def save(self, key, value):
            pass

        def delete(self, key, value):
            pass

        def fetch(self, key):
            raise ValueError()

        def close(self):
            pass

    @settings(database=BadDatabase(), phases=(Phase.generate,))
    @given(st.integers())
    def test_usage(i):
        pass

    test_usage()


def test_will_save_when_reuse_not_in_phases():
    database = InMemoryExampleDatabase()

    assert not database.data

    @settings(database=database, phases=(Phase.generate,))
    @given(st.integers())
    def test_usage(i):
        raise ValueError()

    with pytest.raises(ValueError):
        test_usage()

    (saved,) = (v for k, v in database.data.items() if b"pareto" not in k)
    assert len(saved) == 1


def test_rejects_non_phases():
    with pytest.raises(InvalidArgument):
        settings(phases=["cabbage"])
