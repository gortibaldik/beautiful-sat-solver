
def debug_str(lit_int, itv):
  return f"{'' if lit_int & 1 == 0 else 'NOT '}{itv[lit_int >> 1]}"

def debug_str_multi(multi, itv):
  s = []
  for l in multi:
    s.append(debug_str(l, itv))
  return s

def lit_is_satisfied(lit_int, assignment):
  # positive literals are on even indices
  # therefore for positive literal lit_int & 1 == 0
  # hence (lit_int & 1) ^ 1 == 1 which is a value
  # which we expect from the assigned variable
  return assignment[lit_int >> 1] == ((lit_int & 1) ^ 1)

def lit_is_unsatisfied(lit_int, assignment):
  # positive literals are on even indices
  # therefore for positive literal lit_int & 1 == 0
  # hence lit_int & 1 == 0 which is a value
  # which we expect from the assigned variable
  return assignment[lit_int >> 1] == (lit_int & 1)

def lit_is_none(lit_int, assignment):
  return assignment[lit_int >> 1] is None

def lit_is_assigned(lit_int, assignment):
  return assignment[lit_int >> 1] is not None

def satisfy_lit(lit_int, assignment):
  assignment[lit_int >> 1] = ((lit_int & 1) ^ 1)

def unassign_lit(lit_int, assignment):
  assignment[lit_int >> 1] = None
