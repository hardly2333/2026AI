import numpy as np
import math
import array
import time
import os

# ========== 常量 ==========
PATTERN_TILES = [1,2,3,4,5,9]
# 映射: 0->0, 1->1, 2->2, 3->3, 4->4, 5->5, 9->6
VALUE_MAP = {0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 9:6}
INV_MAP = {0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:9}

TOTAL_COMB = math.comb(16, 7)         # 11440
TOTAL_PERM = math.factorial(7)        # 5040
TOTAL_STATES = TOTAL_COMB * TOTAL_PERM

# 空白邻居
NEIGHBORS = [
    [1,4], [0,2,5], [1,3,6], [2,7],
    [0,5,8], [1,4,6,9], [2,5,7,10], [3,6,11],
    [4,9,12], [5,8,10,13], [6,9,11,14], [7,10,15],
    [8,13], [9,12,14], [10,13,15], [11,14]
]

# ========== 组合数表 C[n][k] (0<=n<=16, 0<=k<=7) ==========
C = np.zeros((17, 8), dtype=np.int32)
for n in range(17):
    C[n][0] = 1
    for k in range(1, min(n, 7)+1):
        C[n][k] = C[n-1][k-1] + C[n-1][k]

# ========== 组合 rank / unrank ==========
def comb_rank(comb):
    """comb: 升序7个位置"""
    r = 0
    prev = -1
    for i, x in enumerate(comb):
        for j in range(prev+1, x):
            r += C[15-j][6-i]
        prev = x
    return r

def comb_unrank(rank):
    comb = []
    prev = -1
    for i in range(7):
        for j in range(prev+1, 16):
            c = C[15-j][6-i]
            if rank >= c:
                rank -= c
            else:
                comb.append(j)
                prev = j
                break
    return comb

# ========== 排列 rank / unrank ==========
FACT = [1, 1, 2, 6, 24, 120, 720, 5040]

def perm_rank(perm):
    r = 0
    for i in range(7):
        x = perm[i]
        smaller = 0
        for j in range(i+1, 7):
            if perm[j] < x:
                smaller += 1
        r += smaller * FACT[6-i]
    return r

def perm_unrank(rank):
    perm = []
    avail = list(range(7))
    for i in range(7):
        f = FACT[6-i]
        idx = rank // f
        rank %= f
        perm.append(avail.pop(idx))
    return perm

# ========== 预计算所有表 ==========
def build_tables():
    print("Building combination tables...")
    comb_list = [comb_unrank(r) for r in range(TOTAL_COMB)]
    comb_dict = {tuple(c): r for r, c in enumerate(comb_list)}

    # comb_idx_table: 每个组合中每个物理位置的索引 (0..6) 或 -1
    comb_idx_table = np.full((TOTAL_COMB, 16), -1, dtype=np.int8)
    for r, comb in enumerate(comb_list):
        for idx, pos in enumerate(comb):
            comb_idx_table[r, pos] = idx

    # comb_move_out_table[R_comb, b_idx, nb] -> new_R_comb
    # new_blank_idx_table[R_comb, b_idx, nb] -> new_blank_idx
    comb_move_out_table = np.zeros((TOTAL_COMB, 7, 16), dtype=np.int32)
    new_blank_idx_table = np.full((TOTAL_COMB, 7, 16), -1, dtype=np.int8)
    for r, comb in enumerate(comb_list):
        for b_idx in range(7):
            p_blank = comb[b_idx]
            for nb in range(16):
                if nb in comb:
                    continue
                new_comb = [x for x in comb if x != p_blank] + [nb]
                new_comb.sort()
                new_r = comb_dict[tuple(new_comb)]
                comb_move_out_table[r, b_idx, nb] = new_r
                new_blank_idx_table[r, b_idx, nb] = new_comb.index(nb)

    print("Building permutation tables...")
    perm_tuples = [tuple(perm_unrank(r)) for r in range(TOTAL_PERM)]
    perm_rank_of_tuple = {p: r for r, p in enumerate(perm_tuples)}
    blank_idx_of_perm = np.array([p.index(0) for p in perm_tuples], dtype=np.uint8)

    # swap_table
    swap_table = np.zeros((TOTAL_PERM, 7, 7), dtype=np.int32)
    for r, p in enumerate(perm_tuples):
        pl = list(p)
        for i in range(7):
            for j in range(7):
                if i == j:
                    swap_table[r, i, j] = r
                else:
                    pl2 = pl.copy()
                    pl2[i], pl2[j] = pl2[j], pl2[i]
                    swap_table[r, i, j] = perm_rank_of_tuple[tuple(pl2)]

    # move_out_table[R_perm, new_b_idx] -> new_R_perm
    move_out_table = np.zeros((TOTAL_PERM, 7), dtype=np.int32)
    for r, p in enumerate(perm_tuples):
        b = p.index(0)
        p_no_0 = list(p)
        p_no_0.pop(b)
        for nb in range(7):
            inserted = p_no_0[:]
            inserted.insert(nb, 0)
            move_out_table[r, nb] = perm_rank_of_tuple[tuple(inserted)]

    return (comb_list, comb_idx_table, comb_move_out_table, new_blank_idx_table,
            perm_tuples, blank_idx_of_perm, swap_table, move_out_table)

# ========== BFS 构建 ==========
def build_pdb(db_path=None):
    if db_path is None:
        db_path = os.path.join(os.path.dirname(__file__), 'pdb.npy')
    # 目标状态
    target_comb = [0,1,2,3,4,8,15]         # 0,1,2,3,4,9,空
    target_perm = [1,2,3,4,5,6,0]           # 1,2,3,4,5,9,空
    target_comb_r = comb_rank(target_comb)
    target_perm_r = perm_rank(target_perm)
    target_rank = target_comb_r * TOTAL_PERM + target_perm_r

    (comb_list, comb_idx_table, comb_move_out_table, new_blank_idx_table,
     perm_tuples, blank_idx_of_perm, swap_table, move_out_table) = build_tables()

    # 距离数组: uint8, 255 表示未访问
    print(f"Allocating distance array: {TOTAL_STATES} bytes ({TOTAL_STATES/1e6:.1f} MB)")
    distance = np.full(TOTAL_STATES, 255, dtype=np.uint8)
    distance[target_rank] = 0

    # 使用双数组交替作为当前层/下一层
    front = array.array('I', [target_rank])
    d = 0
    while len(front) > 0:
        d += 1
        next_front = array.array('I')
        t0 = time.time()
        # 局部变量加速
        dist = distance
        swap = swap_table
        move_out = move_out_table
        c_list = comb_list
        c_move = comb_move_out_table
        nb_idx = new_blank_idx_table
        c_idx = comb_idx_table
        b_idx_of_perm = blank_idx_of_perm

        for rank in front:
            Rc = rank // TOTAL_PERM
            Rp = rank % TOTAL_PERM
            comb = c_list[Rc]
            b_idx = b_idx_of_perm[Rp]
            p_blank = comb[b_idx]
            for nb in NEIGHBORS[p_blank]:
                c = c_idx[Rc, nb]
                if c != -1:                     # 与特殊块交换
                    new_Rp = swap[Rp, b_idx, c]
                    new_rank = Rc * TOTAL_PERM + new_Rp
                else:                           # 移入无关块
                    new_Rc = c_move[Rc, b_idx, nb]
                    new_nb_idx = nb_idx[Rc, b_idx, nb]
                    new_Rp = move_out[Rp, new_nb_idx]
                    new_rank = new_Rc * TOTAL_PERM + new_Rp
                if dist[new_rank] == 255:
                    dist[new_rank] = d
                    next_front.append(new_rank)

        front = next_front
        print(f"Layer {d}: {len(front)} states, time {time.time()-t0:.2f}s")

    print(f"Saving database to {db_path}")
    np.save(db_path, distance)
    print("Done.")

if __name__ == '__main__':
    build_pdb()