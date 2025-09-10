from open_encroachment.utils.geo import point_in_polygon


def test_point_in_polygon_square():
    # Square around (0,0)
    square = [(-1, -1), (-1, 1), (1, 1), (1, -1)]
    assert point_in_polygon(0.0, 0.0, square) is True
    assert point_in_polygon(2.0, 2.0, square) is False
