def assign_variable_to_structures(
    variable,
    itv, # int to variable name
    vti, # variable to int
    assignment,
    itc, # int to clauses
):
    if len(variable.children) != 0:
        raise RuntimeError(f"`{str(variable)}` is supposed to be a variable")
    var_name = str(variable)
    if var_name not in vti:
        var_int = len(assignment)
        vti[var_name] = var_int
        itv.append(var_name)
        assignment.append(None)
        itc.append([])
        itc.append([])
    
    return vti[var_name]

def assign_literal_to_structures(
    literal,
    itv, # int to variable name
    vti, # variable to int
    assignment,
    itc, # int to clauses
):
    # it is a positive literal
    if len(literal.children) == 0:
        # vix == variable index
        vix = assign_variable_to_structures(
            literal,
            itv,
            vti,
            assignment,
            itc
        )
        return vix << 1
    elif len(literal.children) == 1:
        vix = assign_variable_to_structures(
            literal.children[0],
            itv,
            vti,
            assignment,
            itc,
        )
        return vix << 1 | 1
    else:
        raise RuntimeError(f"`{str(literal)}` is supposed to be a literal")
