
import numpy as np
import itertools
from scipy.spatial.distance import cdist


def calculate_distance(point1, point2):
    '''
    計算兩點之間的距離。
    point1: 第一個點的座標
    point2: 第二個點的座標
    return: 兩點之間的距離
    '''
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5


def find_elements(matrix, target_category, target_points):
    '''
    找出符合條件的元素。
    matrix: 二維陣列(3*5)
    target_category: 目標類別
    target_points: 目標點數
    '''
    indices = list(zip(
        *np.where((matrix[:, :, 0] == target_category) & (matrix[:, :, 1] == target_points))))
    # 將每個項都加上固定的數
    result = [(index[0], index[1]) for index in indices]
    return result


def find_single_connections(array_A, array_B):
    '''
    找出A到B的連線 (A和B中的座標不會相同)
    array_A: 陣列A
    array_B: 陣列B
    return: 所有連線
    '''
    # 檢查A和B中的座標是否相同
    unique_A_array = np.unique(array_A, axis=0)
    unique_B_array = np.unique(array_B, axis=0)

    # 初始化結果陣列
    result = []

    # 計算點之間的距離矩陣
    distance_matrix = cdist(unique_A_array, unique_B_array)

    # 對距離矩陣進行排序，獲取排序後的索引
    sorted_indices = np.argsort(distance_matrix, axis=None)

    # 遍歷排序後的索引，添加連接到結果陣列
    for idx in sorted_indices:
        i, j = np.unravel_index(idx, distance_matrix.shape)

        # 排除相同座標點相連的情況
        if not np.array_equal(unique_A_array[i], unique_B_array[j]):
            if not np.array_equal(unique_A_array[i], unique_B_array[j]):
                distance = distance_matrix[i, j]  # 获取距离信息
                # print(distance)
            result.append((unique_A_array[i], unique_B_array[j], distance))
    # 修改座標數組為元組
    result = [(tuple(conn[0]), tuple(conn[1]), conn[2]) for conn in result]

    final_path = []
    used = set()
    # 遍歷 trajectory（或 result，根據你的需要選擇）
    for i in range(len(result)):  # 或者 for conn in result:
        # 如果座標不在 used 集合中，則添加到 final_path 和 used 中
        if result[i][0] not in used and result[i][1] not in used:
            final_path.append(result[i])
            # print(result[i])
            used.add(result[i][0])
            used.add(result[i][1])
    return final_path
import itertools

def find_mult_connections(array_A, array_B):
    '''
    找出所有A到B的連線 (B中座標可複選)
    array_A: 陣列A
    array_B: 陣列B
    return: 所有連線
    '''
    # 找出所有的連線
    path = []
    # 找出A[0]與B的所有連線距離
    for A in array_A:
        connections = []
        for i in range(len(array_B)):
            # connections.append(
            #     (array_A[0][0], array_B[i][0], calculate.distance(array_A[0][1], array_B[i][1])))
            connections.append(
                (A, array_B[i], calculate_distance(A, array_B[i])))
        path.append(sorted(connections, key=lambda x: x[2])[0])

    return path
