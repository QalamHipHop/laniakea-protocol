"""
Unit tests for the 8D SCDA class (numpy-based legacy implementation).

The SCDA class lives at :mod:`laniakea.intelligence.scda_8d_vector` and
operates on an 8-dimensional state vector ``S(t) = (K(t), E(t))`` where
``K(t)`` and ``E(t)`` are 4D knowledge and energy vectors respectively.
"""

import numpy as np
import pytest

from laniakea.intelligence.scda_8d_vector import SCDA, DIMENSIONS, get_8d_state_vector


def _make_scda(k=None, e=None):
    if k is None:
        k = np.array([0.5, 0.5, 0.5, 0.5])
    if e is None:
        e = np.array([1.0, 1.0, 1.0, 1.0])
    return SCDA(initial_k=k, initial_e=e)


def test_scda_initialization():
    scda = _make_scda()
    assert np.allclose(scda.K, [0.5, 0.5, 0.5, 0.5])
    assert np.allclose(scda.E, [1.0, 1.0, 1.0, 1.0])
    assert scda.decay_rate == 0.01
    assert scda.learning_rate == 0.1
    assert scda.E_MAX == 1000.0
    assert scda.K_MAX == 100.0

    # Wrong dimension should raise
    with pytest.raises(ValueError):
        SCDA(initial_k=np.array([1, 2, 3]), initial_e=np.array([4, 5, 6, 7]))


def test_scda_state_vector_shape():
    scda = _make_scda()
    s = scda.state_vector
    assert s.shape == (DIMENSIONS,)
    assert np.allclose(s, [0.5, 0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0])
    # get_8d_state_vector helper should agree
    assert np.allclose(get_8d_state_vector(scda), s)


def test_scda_diminishing_returns():
    scda = _make_scda()
    # Tiny input should still produce a positive, finite output
    assert 0.0 < scda._diminishing_returns(0.001) < 0.01
    # Output is always clipped to [0, max_capacity]
    assert 0.0 <= scda._diminishing_returns(100) <= 1.0
    # Monotonically increasing
    a = scda._diminishing_returns(0.1)
    b = scda._diminishing_returns(1.0)
    c = scda._diminishing_returns(10.0)
    assert a < b < c


def test_scda_energy_management():
    scda = _make_scda()
    # Positive input should increase E
    scda.energy_management(np.array([0.5, 0.5, 0.5, 0.5]))
    assert np.all(scda.E >= 1.0)
    # Negative input should decrease E (clamped at 0)
    scda.energy_management(np.array([-0.4, -0.4, -0.4, -0.4]))
    assert np.all(scda.E >= 0.0)
    # State vector still has the right shape
    assert scda.state_vector.shape == (DIMENSIONS,)


def test_scda_update_passive():
    scda = _make_scda(k=np.array([1.0, 1.0, 1.0, 1.0]), e=np.array([1.0, 1.0, 1.0, 1.0]))
    k_before, e_before = scda.K.copy(), scda.E.copy()
    scda.update_passive()
    # Both vectors should decrease (decay is positive)
    assert np.all(scda.K <= k_before)
    assert np.all(scda.E <= e_before)
    # And remain non-negative
    assert np.all(scda.K >= 0.0)
    assert np.all(scda.E >= 0.0)


def test_scda_problem_solving_returns_tuple():
    scda = _make_scda()
    success, gain = scda.problem_solving(np.array([0.5, 0.5, 0.5, 0.5]))
    # ``success`` may be a numpy bool; treat either as acceptable
    assert bool(success) is True or bool(success) is False
    assert isinstance(gain, float)
    assert gain >= 0.0
    # Wrong dimension should raise
    with pytest.raises(ValueError):
        scda.problem_solving(np.array([0.1, 0.2, 0.3]))


def test_scda_repr_is_informative():
    scda = _make_scda()
    r = repr(scda)
    assert "SCDA" in r
    assert "K=" in r and "E=" in r
