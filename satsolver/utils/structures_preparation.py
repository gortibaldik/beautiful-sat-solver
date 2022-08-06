from satsolver.utils.representation import SATLiteral, SATVariable

def get_literal_int(literal: SATLiteral):
  is_positive = literal.positive
  if is_positive:
    lit_int = literal.satVariable.positive_int
    other_int = literal.satVariable.negative_int
  else:
    lit_int = literal.satVariable.negative_int
    other_int = literal.satVariable.positive_int
  return lit_int, other_int, is_positive

def assign_variable_to_structures(
    variable,
    vti, # variable to int
    itl, # int to literal
    itc, # int to clauses
    create_sat_literal_f = SATLiteral
):
    if len(variable.children) != 0:
        raise RuntimeError(f"`{str(variable)}` is supposed to be a variable")
    var_name = str(variable)
    if var_name not in vti:
        var_int = len(itl)
        vti[var_name] = (var_int, var_int + 1)
        variable = SATVariable(var_int, var_int + 1, var_name)
        itl.append(create_sat_literal_f(variable, True))
        itl.append(create_sat_literal_f(variable, False))
        itc.append([])
        itc.append([])
    
    return vti[var_name]

def assign_literal_to_structures(
    literal,
    vti, # variable to int
    itl, # int to literal
    itc, # int to clauses
    create_sat_literal_f = SATLiteral
):
    # it is a positive literal
    if len(literal.children) == 0:
        pos_int, neg_int = assign_variable_to_structures(
            literal,
            vti,
            itl,
            itc,
            create_sat_literal_f=create_sat_literal_f
        )
        return pos_int
    elif len(literal.children) == 1:
        pos_int, neg_int = assign_variable_to_structures(
            literal.children[0],
            vti,
            itl,
            itc,
            create_sat_literal_f=create_sat_literal_f
        )
        return neg_int
    else:
        raise RuntimeError(f"`{str(literal)}` is supposed to be a literal")