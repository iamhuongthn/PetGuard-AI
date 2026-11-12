import pytest
from src.zone import validate_polygon, is_violation
from src.temporal import TemporalConfirm

ZONE=[(100,100),(300,100),(300,300),(100,300)]

def test_polygon_valid(): assert validate_polygon(ZONE,(640,480))
@pytest.mark.parametrize('points',[
    [(100,100),(300,300),(100,300),(300,100)], # bow tie
    [(100,100),(300,100),(300,100),(100,300)], # duplicate
    [(100,100),(110,100),(110,101)], # tiny
    [(100,100),(700,100),(300,300)] # out of bounds
])
def test_invalid_polygons(points):
    with pytest.raises(ValueError):validate_polygon(points,(640,480))

def test_furniture_overlap():
    assert is_violation((150,150,250,250),ZONE,(480,640,3),'overlap')
    assert not is_violation((350,150,450,250),ZONE,(480,640,3),'overlap')

def test_boundary_inclusive():
    assert is_violation((90,100,110,100),ZONE,(480,640,3),'floor')

def test_scene_level_temporal_and_clearing():
    state=TemporalConfirm(frames_required=5,clear_frames=5)
    for _ in range(4):assert state.update(True)==(False,False)
    assert state.update(True)==(True,True)
    assert state.update(False)==(True,False)
    for _ in range(4):state.update(False)
    assert state.active is False
    assert state.update(False)==(False,False)
