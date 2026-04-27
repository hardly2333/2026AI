from heapq import heappush, heappop

GOAL = (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0)

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

# todo
def is_solvable(state):
    return 1

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

def a_star(puzzle):
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
    closed = set()

    f_start = manhatten(start)
    heappush(open_heap,(f_start,0,start))
    
    while open_heap:
        f_cur, g_cur, state_cur = heappop(open_heap)
        if state_cur in closed and g_cur > g_scores.get(state_cur,float('inf')):
            continue
        if state_cur == GOAL:
            # 回溯
            path = []
            while parents[state_cur][0] is not None:
                path.append(parents[state_cur][1])
                state_cur = parents[state_cur][0]
            path.reverse()
            return path
        closed.add(state_cur)
        neighbours = get_neighbours(state_cur)
        for next_state, moved_number in neighbours:
            if next_state in closed and g_cur + 1 >= g_scores[next_state]:
                continue
            parents[next_state] = (state_cur, moved_number)
            g_scores[next_state] = g_cur + 1
            f_new = manhatten(next_state) + g_cur + 1
            heappush(open_heap,(f_new,g_cur+1,next_state))
    return []

if __name__ == "__main__":
    puzzle = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[0,13,14,15]]
    print(a_star(puzzle))      # 应输出 [13,14,15]
#     print(IDA_star(puzzle))    # 应输出 [13,14,15]