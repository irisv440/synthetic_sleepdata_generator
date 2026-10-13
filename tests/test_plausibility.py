# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 20:45:23 2026

Plausibility tests for the synthetic sleep data generator.

These tests check that the generated data never contain values that are
physically impossible (e.g. negative sleep time) or implausible (e.g. an
extremely long time in bed), for both the control and the insomnia group.

@author: irisv
"""

from pathlib import Path

import pytest

from natale2009_based_synthetic_data_generator import generate_time_series_sleepdata as generate_basic
from natale2009_advanced_generator import generate_time_series_sleepdata as generate_advanced

base_path = Path(__file__).resolve().parent.parent

# Plausible range for time in bed, in minutes (0 to 14 hours)
TIB_MIN = 0
TIB_MAX = 14 * 60

GENERATORS = {"basic": generate_basic, "advanced": generate_advanced}
GROUPS = ["control", "insomnia"]


@pytest.fixture(
    params=[(gen, group) for gen in GENERATORS for group in GROUPS],
    ids=lambda p: f"{p[0]}-{p[1]}",)
def sleepdata(request, tmp_path):
    """Generate synthetic sleep data for one generator and one group, written to a temporary folder."""
    gen_name, group = request.param
    generate = GENERATORS[gen_name]
    parameter_path = base_path / f"input/natale2009_{group}_group_sleep_main_parameters.xlsx"
    output_path = tmp_path / f"synthetic_{group}.xlsx"
    return generate(parameter_path, output_path)


def test_tst_never_negative(sleepdata):
    assert (sleepdata["TST"] >= 0).all()


def test_se_between_0_and_100(sleepdata):
    assert sleepdata["SE"].between(0, 100).all()


def test_tst_not_larger_than_tib(sleepdata):
    assert (sleepdata["TST"] <= sleepdata["TIB"]).all()


def test_tib_within_plausible_range(sleepdata):
    assert sleepdata["TIB"].between(TIB_MIN, TIB_MAX).all()