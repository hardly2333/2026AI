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
    for clause in kb:
        history.append({'id':len(history)+1,'clause':clause, 'source': 'Original'})
    ## pre
    for item in history:
        print(f"{item['id']} {format_clause(item['clause'])}")
    ## i -> new
    i=0
    while i < len(history):
        # j -> old 
        # try single_step(i,j)
        for j in range(i):
            result, idx_i, idx_j, sub = single_step(history[i]['clause'], history[j]['clause'])
            if result is not None:
                if any(result == item['clause'] for item in history):
                    continue
                # shape like R[1a, 2b]
                str_i = get_clause(history[i]['id'], idx_i, history[i]['clause'])
                str_j = get_clause(history[j]['id'], idx_j, history[j]['clause'])
                src_str = f"R[{str_i}, {str_j}]"
                if sub:
                    items = [f"{clean_name(k)}={format_term(v)}" for k, v in sub.items()]
                    src_str += "{" + ",".join(items) + "}"
                new_node = {
                    'id': len(history) + 1,
                    'clause': result,
                    'source': src_str
                }
                history.append(new_node)
                print(f"{new_node['id']} {new_node['source']} = {format_clause(result)}")
                if len(result) == 0:
                    print("Empty clause derived. Proof complete.")
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