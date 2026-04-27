import Convert_input as ci
import MGU as mgu

def format_clause(clause):
    if not clause:
        return "()"
    result = []
    for neg, pred, args in clause:
        sign = "~" if neg else ""
        arg_str = ",".join(format_term(arg) for arg in args)
        result.append(f"{sign}{pred}({arg_str})")
    
    if (len(result) == 1):
        return f"({result[0]},)"
    else:
        return "(" + ",".join(result) + ")"

def format_term(term):
    if isinstance(term, str):
        return clean_name(term)
    elif isinstance(term, tuple):
        func, args = term
        arg_str = ",".join(format_term(arg) for arg in args)
        return f"{func}({arg_str})"

def clean_name(name):
    if isinstance(name, str) and "_" in name:
        return name.split("_")[0]
    return name

def rename(term, suffix):
    if isinstance(term, str):
        if ci.is_variable(term):
            return term + suffix
        return term
    elif isinstance(term, tuple):
        if len(term) == 3:
            neg, pred, args = term
            new_args = tuple(rename(arg, suffix) for arg in args)
            return (neg, pred, new_args)
        elif len(term) == 2:
            func, args = term
            new_args = tuple(rename(arg, suffix) for arg in args)
            return (func, new_args)
    else:
        return term

def rename_clause(clause, suffix):
    return tuple(rename(term, suffix) for term in clause)

def single_step(clause1, clause2):
    c1 = rename_clause(clause1, '_1')
    c2 = rename_clause(clause2, '_2')
    for i, term1 in enumerate(c1):
        for j, term2 in enumerate(c2):
            if term1[0] != term2[0] and term1[1] == term2[1]: 
                # P(x) , ~P(a)
                substitution = mgu.MGU(term1, term2)
                # sub = {x: a}
                if substitution is not None:
                    # unify, remove t1 t2
                    rest = []
                    for t, lit in enumerate(c1):
                        if t != i : rest.append(lit)
                    for t, lit in enumerate(c2):
                        if t != j : rest.append(lit)
                    # apply sub to rest
                    new_clause = []
                    for lit in rest:
                        new_lit = mgu.apply_dict(lit, substitution)
                        if new_lit not in new_clause:
                            new_clause.append(new_lit)
                    return tuple(new_clause), i , j, substitution
    return None, None, None, None

def solve(kb):
    history = []
    ## add id for each clause -> eg. { 'id': 1, 'clause': ('P(x)', '~Q(x)'), 'source': 'Original' }
    ## add BFS feature: level, parent_ids
    for clause in kb:
        history.append({'id':len(history)+1,
                        'clause':clause, 
                        'source': 'Original',
                        'level': 0,
                        'parent_ids': None})
    ## i -> new
    curr_level = 0
    i=0
    while i < len(history):
        # use bfs, always try history[i] and history[j],
        # then choose clause with smaller level
        # j -> old 
        # try single_step(i,j)
        for j in range(i):
            result, idx_i, idx_j, sub = single_step(history[i]['clause'], history[j]['clause'])
            parent1_node = history[i]
            parent2_node = history[j]
            if result is not None:
                if any(result == item['clause'] for item in history):
                    continue
                new_level = max(parent1_node['level'], parent2_node['level']) + 1
                # shape like R[1a, 2b]
                str_i = get_clause(history[i]['id'], idx_i, history[i]['clause'])
                str_j = get_clause(history[j]['id'], idx_j, history[j]['clause'])
                src_str = f"R[{str_i}, {str_j}]"
                if sub:
                    items = [f"{clean_name(k)}={format_term(v)}" for k, v in sub.items()]
                    src_str += "{" + ",".join(items) + "}"
                new_step = {
                    'id': len(history) + 1,
                    'clause': result,
                    'source': src_str,
                    'level': new_level,
                    'parent_ids': (history[i]['id'], history[j]['id']),
                    'idx': (idx_i, idx_j),
                    'sub': sub
                }
                history.append(new_step)
##                print(f"{new_step['id']} {new_step['source']} = {format_clause(result)}")
                if len(result) == 0:
                    print_shortest_path(history, new_step)
                    return True
        i += 1
        if len(history) > 500:
            break
    return False

def get_clause(clause_id, index, clause_tuple):
    # one term in a clause, return str
    if len(clause_tuple) == 1:
        return str(clause_id)
    # more than one id+alpha
    else:
        char = chr(ord('a') + index)
        return f"{clause_id}{char}"

def print_shortest_path(history, last_step):
    ## only print useful step from empty clause to original clause
    path_step_ids = set()
    def search(curr_step):
        if curr_step['id'] in path_step_ids:
            return
        path_step_ids.add(curr_step['id'])
        if curr_step['parent_ids'] is not None:
            p1_id, p2_id = curr_step['parent_ids']
            # find parent step in history
            p1 = next(s for s in history if s['id'] == p1_id)
            p2 = next(s for s in history if s['id'] == p2_id)
            search(p1)
            search(p2)
            
    search(last_step)
    # sort and re-number
    sorted_ids = sorted(list(path_step_ids))
    id_map = {old_id: i + 1 for i, old_id in enumerate(sorted_ids)}
    
    print("\nTest_Start !")
    for old_id in sorted_ids:
        # find default ids
        curr = next(s for s in history if s['id'] == old_id)
        new_id = id_map[old_id]
        if curr['parent_ids'] is None:
            # original clause
            print(f"{new_id} {format_clause(curr['clause'])}")
        else:
            # has parent, need to find parent clause and idx
            p1_old_id, p2_old_id = curr['parent_ids']
            idx1, idx2 = curr['idx']
            # get original clause for parent
            p1_orig = next(s for s in history if s['id'] == p1_old_id)
            p2_orig = next(s for s in history if s['id'] == p2_old_id)
            # check whether to use 1a or 1 
            c1 = get_clause(id_map[p1_old_id], idx1, p1_orig['clause'])
            c2 = get_clause(id_map[p2_old_id], idx2, p2_orig['clause'])
            source = f"R[{c1},{c2}]"
            # clean x_1 to x
            if curr['sub']:
                sub_items = [f"{clean_name(k)}={format_term(v)}" for k, v in curr['sub'].items()]
                source += "{" + ",".join(sub_items) + "}"
            print(f"{new_id} {source} = {format_clause(curr['clause'])}")