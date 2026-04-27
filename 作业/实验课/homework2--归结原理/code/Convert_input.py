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
    