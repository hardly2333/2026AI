from functools import lru_cache
from collections import deque
from heapq import heappush, heappop
import math
import sys
import os
from time import perf_counter
import numpy as np
# IDA* 递归深度可能较大，适当提高递归上限。
sys.setrecursionlimit(2000)

# 目标状态：按 1 到 15 排列，空格 0 放在最后。
GOAL = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0)

PATTERN_FACT = (1, 1, 2, 6, 24, 120, 720, 5040)
PDB_PATH = os.path.join(os.path.dirname(__file__), "pdb.npy")
_PDB = None

# 非可加性模式数据库使用的模式：只跟踪这 7 个数字和空格的位置。
PATTERN_TILES = (1, 2, 3, 4, 5, 9)
PATTERN_INDEX = {tile: index for index, tile in enumerate(PATTERN_TILES)}
PATTERN_ADJACENT = tuple(
    tuple(
        neighbour
        for neighbour in (
            cell - 4 if cell >= 4 else None,
            cell + 4 if cell < 12 else None,
            cell - 1 if cell % 4 != 0 else None,
            cell + 1 if cell % 4 != 3 else None,
        )
        if neighbour is not None
    )
    for cell in range(16)
)

# example
# puzzle = [[1,2,4,8],[5,7,11,10],[13,15,0,3],[14,6,9,12]]
# puzzle = [[14,10,6,0],[4,9,1,8],[2,3,5,11],[12,13,7,15]]
# puzzle = [[5,1,3,4],[2,7,8,12],[9,6,11,15],[0,13,10,14]]
# puzzle = [[6,10,3,15],[14,8,7,11],[5,1,0,2],[13,12,9,4]]
# puzzle = [[11,3,1,7],[4,6,8,2],[15,9,10,13],[14,12,5,0]]
# puzzle = [[0,5,15,14],[7,9,6,13],[1,2,12,10],[8,11,4,3]]

def flatten(puzzle):
    # 将 4x4 矩阵展开成一维状态元组，便于哈希、缓存和搜索。
    return tuple(puzzle[i][j] for i in range(4) for j in range(4))

##################################################
# 启发式函数
##################################################

# 曼哈顿距离启发式：估计每个数字到目标位置的横纵距离之和。
@lru_cache(maxsize=None)
def manhatten(state):
    total = 0
    for idx, val in enumerate(state):
        if val == 0 :
            continue
        target_idx = val-1
        cur_i, cur_j = divmod(idx, 4)
        tar_i, tar_j = divmod(target_idx,4)
        total += abs(cur_i - tar_i) + abs(cur_j - tar_j)
    return total

# 线性冲突：在曼哈顿距离基础上额外惩罚同一行/列中的逆序块。
@lru_cache(maxsize=None)
def linear_conflict(state):
    conflict = 0
    # 行冲突
    for i in range(4):
        row_vals = []
        for j in range(4):
            val = state[i*4 + j]
            if val == 0:
                continue
            target_i = (val-1) // 4
            if target_i == i:
                target_j = (val-1) % 4
                row_vals.append((j,target_j))
        for a in range(len(row_vals)):
            for b in range(a+1, len(row_vals)):
                if (row_vals[a][0] < row_vals[b][0] and row_vals[a][1] > row_vals[b][1]) or \
                (row_vals[a][0] > row_vals[b][0] and row_vals[a][1] < row_vals[b][1]):
                    conflict += 2
    # 列冲突
    for j in range(4):
        col_vals = []
        for i in range(4):
            val = state[i*4 + j]
            if val == 0:
                continue
            target_j = (val-1) % 4
            if target_j == j:
                target_i = (val-1) // 4
                col_vals.append((i,target_i))
        for a in range(len(col_vals)):
            for b in range(a+1, len(col_vals)):
                if (col_vals[a][0] < col_vals[b][0] and col_vals[a][1] > col_vals[b][1]) or \
                (col_vals[a][0] > col_vals[b][0] and col_vals[a][1] < col_vals[b][1]):
                    conflict += 2
    return conflict

# Walking Distance：基于每行/列的目标分布预计算的启发式表，能更准确地估计状态距离。
@lru_cache(maxsize=None)
def vertical_signature(state):
    # Walking Distance 的纵向签名：记录每一行里各目标“所属行”的数量分布。
    signature = []
    for row in range(4):
        counts = [0, 0, 0, 0, 0]
        for col in range(4):
            value = state[row * 4 + col]
            if value == 0:
                counts[4] += 1
            else:
                counts[(value - 1) // 4] += 1
        signature.append(tuple(counts))
    return tuple(signature)

@lru_cache(maxsize=None)
def horizontal_signature(state):
    # Walking Distance 的横向签名：记录每一列里各目标“所属列”的数量分布。
    signature = []
    for col in range(4):
        counts = [0, 0, 0, 0, 0]
        for row in range(4):
            value = state[row * 4 + col]
            if value == 0:
                counts[4] += 1
            else:
                counts[(value - 1) % 4] += 1
        signature.append(tuple(counts))
    return tuple(signature)

def build_walking_distance_table(goal_signature):
    # 从目标签名出发做 BFS，预计算 Walking Distance 的状态代价表。
    table = {goal_signature: 0}
    queue = deque([goal_signature])

    while queue:
        state = queue.popleft()
        distance = table[state]
        blank_row = next(index for index, row in enumerate(state) if row[4])

        for delta in (-1, 1):
            neighbour_row = blank_row + delta
            if not (0 <= neighbour_row < 4):
                continue

            neighbour = state[neighbour_row]
            for tile_kind in range(4):
                if neighbour[tile_kind] == 0:
                    continue

                next_rows = [list(row) for row in state]
                next_rows[blank_row][tile_kind] += 1
                next_rows[blank_row][4] -= 1
                next_rows[neighbour_row][tile_kind] -= 1
                next_rows[neighbour_row][4] += 1
                next_state = tuple(tuple(row) for row in next_rows)

                if next_state not in table:
                    table[next_state] = distance + 1
                    queue.append(next_state)

    return table
VERTICAL_WD_TABLE = build_walking_distance_table(vertical_signature(GOAL))
HORIZONTAL_WD_TABLE = build_walking_distance_table(horizontal_signature(GOAL))


##################################################
# 非可加性模式数据库启发式
##################################################

def comb_rank(comb):
    rank = 0
    previous = -1
    for i, position in enumerate(comb):
        for candidate in range(previous + 1, position):
            rank += math.comb(15 - candidate, 6 - i)
        previous = position
    return rank


def perm_rank(perm):
    rank = 0
    for i in range(7):
        smaller = 0
        current = perm[i]
        for j in range(i + 1, 7):
            if perm[j] < current:
                smaller += 1
        rank += smaller * PATTERN_FACT[6 - i]
    return rank


def load_pattern_database():
    global _PDB
    if _PDB is None:
        _PDB = np.load(PDB_PATH, mmap_mode="r")
    return _PDB


def pattern_database_rank(state):
    positions = []
    permutation = []
    for index, value in enumerate(state):
        if value == 0:
            positions.append(index)
            permutation.append(0)
        elif value in PATTERN_INDEX:
            positions.append(index)
            permutation.append(PATTERN_INDEX[value] + 1)

    if len(positions) != 7:
        return 0

    return comb_rank(positions) * 5040 + perm_rank(permutation)


@lru_cache(maxsize=None)
def pattern_database(state):
    pdb = load_pattern_database()
    return int(pdb[pattern_database_rank(state)])




#########################################################################

# 选择启发式函数
@lru_cache(maxsize=None)
def h(state):
    return VERTICAL_WD_TABLE[vertical_signature(state)] + HORIZONTAL_WD_TABLE[horizontal_signature(state)]
    # return manhatten(state)
    # return manhatten(state) + linear_conflict(state)
    # return pattern_database(state)

# 依据 15-puzzle 的逆序数与空格所在行判断状态是否可解。
@lru_cache(maxsize=None)
def is_solvable(state):
    idx = state.index(0)
    row_from_bottom = 4 - (idx // 4)
    seq = [v for v in state if v != 0]
    invert_count = 0 
    for i in range(len(seq)):
        for j in range(i+1, len(seq)):
            if seq[i] > seq[j]:
                invert_count += 1
    return (invert_count % 2) != (row_from_bottom % 2)

# 辅助函数：生成空格与上下左右相邻数字交换后的后继状态，并记录被移动的数字。
def get_neighbours(state):
    idx = state.index(0)
    i, j = divmod(idx,4)
    neighbours = []
    for di, dj in ((-1,0),(1,0),(0,-1),(0,1)):
        ni = i+di
        nj =j+dj
        if 0 <= ni < 4 and 0 <= nj < 4:
            new_idx = 4*ni + nj
            lst = list(state)
            lst[idx], lst[new_idx] = lst[new_idx], lst[idx]
            next_state = tuple(lst)
            moved_number = lst[idx]
            neighbours.append((next_state,moved_number))
    return neighbours

# A*：用优先队列维护 open set，按 f = g + h 扩展最有希望的节点。
def A_star(puzzle, with_stats=False):
    start = flatten(puzzle)
    if start == GOAL:
        return ([], 0, 0.0) if with_stats else []
    if is_solvable(start) == 0:
        return ([], 0, 0.0) if with_stats else []
    start_time = perf_counter()
    
    # open_heap 元素：按 (f, h, g, state) 存储，便于稳定地取出最优节点。
    open_heap = []
    g_scores = {start:0}
    parents = {start:(None, None)}
    expanded_nodes = 0

    f_start = h(start)
    heappush(open_heap,(f_start,f_start,0,start))
    
    while open_heap:
        _, _, g_cur, state_cur = heappop(open_heap)
        if g_cur > g_scores.get(state_cur,float('inf')):
            continue
        expanded_nodes += 1
        if state_cur == GOAL:
            # 目标到达后沿父指针回溯，恢复移动序列。
            path = []
            while parents[state_cur][0] is not None:
                path.append(parents[state_cur][1])
                state_cur = parents[state_cur][0]
            path.reverse()
            if with_stats:
                return path, expanded_nodes, perf_counter() - start_time
            return path
        
        for next_state, moved_number in get_neighbours(state_cur):
            g_new = g_cur + 1
            if g_new >= g_scores.get(next_state, float('inf')):
                continue
            parents[next_state] = (state_cur, moved_number)
            g_scores[next_state] = g_new
            h_new = h(next_state)
            f_new = h_new + g_new
            heappush(open_heap,(f_new, h_new ,g_new ,next_state))
    if with_stats:
        return [], expanded_nodes, perf_counter() - start_time
    return []


# IDA*：以启发式阈值逐步加深，适合较大搜索空间但更省内存。
def IDA_star(puzzle, with_stats=False):
    start = flatten(puzzle)
    if start == GOAL:
        return ([], 0, 0.0) if with_stats else []
    if is_solvable(start) == 0:
        return ([], 0, 0.0) if with_stats else []

    start_time = perf_counter()
    limit = h(start)
    expanded_nodes = 0

    def dfs(state, g, limit_now, path, path_set):
        nonlocal expanded_nodes
        # 深度优先搜索中若 f 超过当前阈值，就把该值作为下一轮的候选下界。
        f = g + h(state)
        if f > limit_now:
            return f

        expanded_nodes += 1
        if state == GOAL:
            return -1

        min_limit = float('inf')
        for next_state, moved_number in get_neighbours(state):
            if next_state in path_set:
                continue

            path.append(moved_number)
            path_set.add(next_state)

            d = dfs(next_state, g + 1, limit_now, path, path_set)
            if d == -1:
                return -1
            if d < min_limit:
                min_limit = d

            path.pop()
            path_set.remove(next_state)

        return min_limit

    while True:
        path = []
        path_set = {start}
        d = dfs(start, 0, limit, path, path_set)

        if d == -1:
            # 找到解后直接返回当前路径。
            if with_stats:
                return path, expanded_nodes, perf_counter() - start_time
            return path

        if d == float('inf'):
            # 没有更优的下一阈值，说明搜索失败。
            if with_stats:
                return [], expanded_nodes, perf_counter() - start_time
            return []

        # 下一轮阈值提升到本轮搜索中遇到的最小超界值。
        limit = d


if __name__ == "__main__":
    # PPT中给的六个测试样例
    EXAMPLES = [
        # [[1,2,4,8],[5,7,11,10],[13,15,0,3],[14,6,9,12]],
        # [[14,10,6,0],[4,9,1,8],[2,3,5,11],[12,13,7,15]],
        # [[5,1,3,4],[2,7,8,12],[9,6,11,15],[0,13,10,14]],
        # [[6,10,3,15],[14,8,7,11],[5,1,0,2],[13,12,9,4]],
        [[11,3,1,7],[4,6,8,2],[15,9,10,13],[14,12,5,0]],
        # [[0,5,15,14],[7,9,6,13],[1,2,12,10],[8,11,4,3]],
    ]

    results_path = os.path.join(os.path.dirname(__file__), "results.txt")
    # 结果文件先写表头，后续逐个追加每个样例的统计信息。
    with open(results_path, "w", encoding="utf-8") as f:
        f.write("id,steps,expanded_nodes,time_seconds\n")

    for i, puzzle in enumerate(EXAMPLES[:5], start=1):
        print(f"Running example {i}...")
        solution, expanded_nodes, elapsed = IDA_star(puzzle, with_stats=True)
        steps = len(solution)
        print(f"Example {i}: 步数={steps}, 扩展节点={expanded_nodes}, 用时={elapsed:.6f}s")

        # 保存每个样例的步数、扩展节点数和耗时
        with open(results_path, "a", encoding="utf-8") as f:
            f.write(f"{i},{steps},{expanded_nodes},{elapsed:.6f}\n")

    print(f"All done. Results written to: {results_path}")