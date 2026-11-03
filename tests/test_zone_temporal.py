"""Fast geometry and temporal tests; no model download required."""
from src.zone import is_violation
from src.temporal import TemporalConfirm

ZONE = [(100, 100), (300, 100), (300, 300), (100, 300)]
SHAPE = (480, 640, 3)

def test_safe():
    assert not is_violation((350, 150, 450, 250), ZONE, SHAPE, "floor")

def test_violation():
    assert is_violation((150, 150, 250, 250), ZONE, SHAPE, "floor")

def test_temporal():
    state = TemporalConfirm(frames_required=5)
    for _ in range(4):
        assert state.update(True) == (False, False)
    assert state.update(True) == (True, True)
    assert state.update(True) == (True, False)
    for _ in range(5):
        state.update(False)
    for _ in range(4):
        assert state.update(True) == (False, False)
    assert state.update(True) == (True, True)
