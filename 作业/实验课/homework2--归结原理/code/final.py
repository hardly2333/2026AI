## this module convert input into what we need
## some difinition:
## variable: x, y, z, w, u, v, xx,yy,zz,ww,uu,vv
## constant: lowercase words & letters excpet var
## atom formula: "~" + predicate + "(" + args + ")"

def is_variable(term):
    variables = ['x', 'y', 'z', 'w', 'u', 'v', "xx","yy", "zz", "uu", "vv", "ww",
                  "x_1", "x_2", "y_1", "y_2","z_1", "z_2", 
                  "w_1", "w_2", "u_1", "u_2", "v_1", "v_2",
                  "xx_1","yy_1","xx_2","yy_2","zz_1","zz_2",
                  "uu_1","uu_2","vv_1","vv_2","ww_1","ww_2"]
    return term in variables

def split_args(args_str):
## use for formula like P(a,f(x,y)), div into args: a, f(x,y)
    result = []
    curr_arg = '' 
    count = 0
    for char in args_str:
        if char == ',' and count == 0:
            result.append(curr_arg.strip())
            curr_arg = ''
        else:
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
            curr_arg += char
    if curr_arg:
        result.append(curr_arg.strip())
    return result

def parse_term(term):
## if term is a const or varible, return
## if term is a func, return shape like (func_name, [args])
    term = term.strip()
    if "(" not in term:
        return term
    else:
        func_name = term[:term.find('(')]
        args_str = term[term.find('(')+1:term.rfind(')')]
        args = split_args(args_str)
        return func_name, tuple(parse_term(arg) for arg in args)

def parse_atom_formula(formula):
## divide atom formula into three parts: ~ , predicate , args
    if formula[0] == '~':
        negative = True
        formula = formula[1:]
    else:
        negative = False
    predicate = formula[:formula.find('(')]
    args_str = formula[formula.find('(')+1:formula.rfind(')')]
    raw_args = split_args(args_str)
    args = tuple(parse_term(arg) for arg in raw_args)
    return negative, predicate, args

def parse_clause(clause):
## divide clause into atom formula, input example (P(x), ~Q(a),)
## important: the last char of clause must be ","
    clause = clause.strip()
    # clean ()
    if clause[0] == '(' and clause[-1] == ')':
        clause = clause[1:-1].strip()
    raw_formulas = split_args(clause)
    parsed_formulas = []
    for formula in raw_formulas:
        formula = formula.strip()
        if formula:
            parsed_formulas.append(parse_atom_formula(formula))
    return tuple(parsed_formulas)

def load_kb(clause_list):
## convert input clause list into a set of clause tuples
    kb = set()
    for clause in clause_list:
        if isinstance(clause, tuple):
            _clause_tuple = clause[0]
        else:
            _clause_tuple = clause
        clause_tuple = parse_clause(_clause_tuple)
        kb.add(clause_tuple)
    return kb

# MGU
# divide into steps:
# 1. apply dict to two terms
# 2. check two terms same or not, if same, return dict
# 3. if one is var, unify var with other term, return new dict
# 4. if two are func, should be shape like (P(x,f(y),z), P(f(a),f(b),c)),
#    it should have same func and nums of args, then unify each arg.
# 5. jmp to 1, until success or fail(None)

def MGU(term1, term2, substitution=None):
    if substitution is None:
        substitution = {}
    return unify(term1, term2, substitution)

def apply_dict(term, substitution):
# step1's func
# apply dict to term, return new term
# example: term = x, substitution = {x: a}, return a
# two kinds: variable and function
    if isinstance(term, str) and is_variable(term):
        return substitution.get(term, term)

    if isinstance(term, tuple):
        if len(term) == 3: 
            neg, pred, args = term
            new_args = tuple(apply_dict(arg, substitution) for arg in args)
            return neg, pred, new_args
        elif len(term) == 2:
            func_name, args = term
            new_args = tuple(apply_dict(arg, substitution) for arg in args)
            return func_name, new_args
    else:
        return term

def unify(term1, term2, substitution):
# step2-5's main check func
# check two terms' relation and choose right way to unify
# unify two terms with given substitution, return new substitution or None
    term1 = apply_dict(term1, substitution)
    term2 = apply_dict(term2, substitution)
    if substitution is None:
        return None
    elif term1 == term2: 
        return substitution
    elif is_variable(term1):
        return unify_var(term1, term2, substitution)
    elif is_variable(term2):
        return unify_var(term2, term1, substitution)
    elif isinstance(term1, tuple) and isinstance(term2, tuple): 
    # tuple can be atom or func, need to check
        if len(term1) == 3 and len(term2) == 3:
            neg1, pred1, args1 = term1
            neg2, pred2, args2 = term2
            if pred1 != pred2 or len(args1) != len(args2):
                return None
            for arg1, arg2 in zip(args1, args2):
                substitution = unify(arg1, arg2, substitution)
                if substitution is None:
                    return None
            return substitution
        elif len(term1) == 2 and len(term2) == 2:
            func1, args1 = term1
            func2, args2 = term2
            if func1 != func2 or len(args1) != len(args2):
                return None
            for arg1, arg2 in zip(args1, args2):
                substitution = unify(arg1, arg2, substitution)
                if substitution is None:
                    return None
            return substitution
    else:
        return None

def unify_var(var, term, substitution):
# step3-4's func, adding new substitution
# unify var with term, return new substitution or None
# example: var = x, term = a, substitution = {}, return {x: a}
    if var in substitution:
        return unify(substitution[var], term, substitution)
    elif is_variable(term) and term in substitution:
        return unify(var, substitution[term], substitution)
    elif occurs_check(var, term, substitution):
        return None
    else:
        new_substitution = {}
        for old_v, old_x in substitution.items():
            new_substitution[old_v] = apply_dict(old_x, {var: term})
        new_substitution[var] = term
        return new_substitution

def occurs_check(var, term, substitution):
# prevent infinite loop, like f(f(f(f(x))))
    if var == term:
        return True
    if isinstance(term, tuple):
        # atom formula (len 3) has args at index 2, function (len 2) at index 1
        args = term[2] if len(term) == 3 else term[1]
        for arg in args:
            if occurs_check(var, arg, substitution):
                return True
    return False

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
        if is_variable(term):
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
                substitution = MGU(term1, term2)
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
                        new_lit = apply_dict(lit, substitution)
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
    ## pre
    for item in history:
        print(f"{item['id']} {format_clause(item['clause'])}")
    ## i -> new
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
                if len(result) == 0:
                    print("Empty clause derived. Proof complete.")
                    print_shortest_path(history, new_step)
                    return True
        i += 1
        if len(history) > 1000:
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

if __name__ == "__main__":
    # --- 测试 Graduate Student 问题 ---
    print("="*20 + " Graduate Student " + "="*20)
    raw_kb1 = [
        "GradStudent(sue)",
        "(~GradStudent(x), Student(x))",
        "(~Student(x), HardWorker(x))",
        "~HardWorker(sue)"
    ]
    kb_list1 = [parse_clause(c) for c in raw_kb1]
    solve(kb_list1)

    # --- 正在解决 Alpine Club 问题 ---
    print("\n" + "="*20 + " Alpine Club " + "="*20)
    alpine_kb = [
        "A(tony)", "A(mike)", "A(john)", "L(tony,rain)", "L(tony,snow)",
        "(~A(x), S(x), C(x))", "(~C(y), ~L(y,rain))", "(L(z,snow), ~S(z))",
        "(~L(tony,u), ~L(mike,u))", "(L(tony,v), L(mike,v))", "(~A(w), ~C(w), S(w))"
    ]
    kb_list2 = [parse_clause(c) for c in alpine_kb]
    solve(kb_list2)

    # --- 开始测试作业 2: 颜色传递问题 ---
    print("\n" + "="*20 + " Color Logic " + "="*20)
    raw_kb3 = [
        "On(tony,mike)", "On(mike,john)", "Green(tony)", "~Green(john)",
        "(~On(xx,yy), ~Green(xx), Green(yy))"
    ]
    kb_list3 = [parse_clause(c) for c in raw_kb3]
    solve(kb_list3)