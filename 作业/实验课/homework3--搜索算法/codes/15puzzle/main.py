from heapq import heappush, heappop
import sys
sys.setrecursionlimit(2000)

GOAL = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0)

# example
# puzzle = [[1,2,4,8],[5,7,11,10],[13,15,0,3],[14,6,9,12]]
# puzzle = [[14,10,6,0],[4,9,1,8],[2,3,5,11],[12,13,7,15]]
# puzzle = [[5,1,3,4],[2,7,8,12],[9,6,11,15],[0,13,10,14]]
puzzle = [[6,10,3,15],[14,8,7,11],[5,1,0,2],[13,12,9,4]]
# puzzle = [[11,3,1,7],[4,6,8,2],[15,9,10,13],[14,12,5,0]]
# puzzle = [[0,5,15,14],[7,9,6,13],[1,2,12,10],[8,11,4,3]]

def flatten(puzzle):
    return tuple(puzzle[i][j] for i in range(4) for j in range(4))

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

def h(state):
    return manhatten(state) + linear_conflict(state)

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

def A_star(puzzle):
    start = flatten(puzzle)
    if start == GOAL:
        return []
    if is_solvable(start) == 0:
        return []
    
    #init
    # open_set 元素: (f,g,state)
    open_heap = []
    g_scores = {start:0}
    parents = {start:(None, None)}

    f_start = h(start)
    heappush(open_heap,(f_start,0,start))
    
    while open_heap:
        f_cur, g_cur, state_cur = heappop(open_heap)
        if g_cur > g_scores.get(state_cur,float('inf')):
            continue
        if state_cur == GOAL:
            # 回溯
            path = []
            while parents[state_cur][0] is not None:
                path.append(parents[state_cur][1])
                state_cur = parents[state_cur][0]
            path.reverse()
            return path
        neighbours = get_neighbours(state_cur)
        for next_state, moved_number in neighbours:
            if g_cur + 1 >= g_scores.get(next_state, float('inf')):
                continue
            parents[next_state] = (state_cur, moved_number)
            g_scores[next_state] = g_cur + 1
            f_new = h(next_state) + g_cur + 1
            heappush(open_heap,(f_new,g_cur+1,next_state))
    return []

def IDA_star(puzzle):
    start = flatten(puzzle)
    if start == GOAL:
        return []
    if is_solvable(start) == 0:
        return []
    limit = h(start)
    path_set = set()
    path = []

    def dfs(state, g, next_limit_ref):
        f = g + h(state)
        if f > limit:
            next_limit_ref[0] = min(next_limit_ref[0],f)
            return False
        if state == GOAL:
            return True
        for next_state, moved_number in get_neighbours(state):
            if next_state in path_set:
                continue
            path.append(moved_number)
            path_set.add(next_state)
            if dfs(next_state, g+1, next_limit_ref):
                return True
            path.pop()
            path_set.remove(next_state)
        return False
    
    while True:
        next_limit = [float('inf')]
        path_set.clear()
        path.clear()
        path_set.add(start)
        if dfs(start, 0, next_limit):
            return path
        if next_limit[0] == float('inf'):
            return []
        limit = next_limit[0]


if __name__ == "__main__":
    print(A_star(puzzle))     
    # print(IDA_star(puzzle))   