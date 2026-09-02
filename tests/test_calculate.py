import numpy as np

from calculate import calculate_distance, find_elements, find_mult_connections


def test_calculate_distance():
    assert calculate_distance((0, 0), (3, 4)) == 5


def test_find_elements_returns_matching_board_positions():
    board = np.array([[[1, 1], [2, 3], [-1, -1]], [[1, 2], [2, 3], [1, 1]], [[3, 1], [1, 1], [2, 4]]])

    assert find_elements(board, 1, 1) == [(0, 0), (1, 2), (2, 1)]


def test_find_mult_connections_chooses_nearest_target_for_each_source():
    result = find_mult_connections([(0, 0), (2, 2)], [(0, 1), (2, 1)])

    assert result[0][0] == (0, 0)
    assert result[0][1] == (0, 1)
    assert result[0][2] == 1
    assert result[1][0] == (2, 2)
    assert result[1][1] == (2, 1)
    assert result[1][2] == 1
