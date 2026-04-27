import Convert_input as ci
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
    if isinstance(term, str) and ci.is_variable(term):
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
    elif ci.is_variable(term1):
        return unify_var(term1, term2, substitution)
    elif ci.is_variable(term2):
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
    elif ci.is_variable(term) and term in substitution:
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
        func_name, args = term
        for arg in args:
            if occurs_check(var, arg, substitution):
                return True
    return False