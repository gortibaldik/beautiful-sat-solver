from collections import deque
from heapq import heappop, heappush
from typing import Deque, List, Set
from satsolver.cdcl.assignment import _def_dec_lvl
from satsolver.utils.representation import debug_str_multi
from satsolver.cdcl.representation import SATClause

def init_literals_from_clause(
  clause: SATClause,
  current_dec_lvl,
  itv,
  dec_lvls_of_vars
):
  priority_queue = []
  # during the preprocessing unit propagation, all the unit propagated
  # variables are assigned dec_lvl 0
  # 
  # during the first real unit propagation, all the unit propagated
  # variables are assigned 1
  highest_dec_lvl = -1
  highest_lit_int = None
  dec_lvl_set     = [False] * (current_dec_lvl + 1)
  dec_lvl_set[current_dec_lvl] = True
  for lit_int in clause.children:
    var_int = lit_int >> 1
    tpl = dec_lvls_of_vars[var_int]
    if tpl[0] == current_dec_lvl:
      if tpl[1] <= 0:
        heappush(priority_queue, (*tpl, lit_int))

        # prevents the dec var to be traversed multiple
        # times
        dec_lvls_of_vars[var_int] = (tpl[0], 1)
    else:
      dec_lvl_set[tpl[0]] = True
      if highest_dec_lvl < tpl[0]:
        highest_dec_lvl = tpl[0]
        highest_lit_int = lit_int

  return priority_queue, highest_dec_lvl, highest_lit_int, dec_lvl_set

def get_literals_from_clause(
  clause: SATClause,
  current_dec_lvl,
  dec_lvls_of_vars,
  priority_queue,
  dec_lvl_set
):
  for lit_int in clause.children:
    var_int = lit_int >> 1
    tpl = dec_lvls_of_vars[var_int]
    if tpl[0] == current_dec_lvl:
      if tpl[1] <= 0:
        heappush(priority_queue, (*tpl, lit_int))

        # prevents the dec var to be traversed multiple
        # times
        dec_lvls_of_vars[var_int] = (tpl[0], 1)
    else:
      dec_lvl_set[tpl[0]] = True

def conflict_analysis(
  conflict_clause: SATClause,
  current_dec_lvl,
  dec_lvls_of_vars,
  antecedents: List[SATClause],
  itv
):
  priority_queue, highest_dec_lvl, highest_lit_int, dec_lvl_set = init_literals_from_clause(
    conflict_clause,
    current_dec_lvl,
    itv,
    dec_lvls_of_vars
  )
  assertive_clause = set(conflict_clause.children)

  # stop at the first UIP
  # hence when len(deq) <= 1
  while len(priority_queue) > 1:
    _, _, lit_int = heappop(priority_queue)
    var_int = lit_int >> 1

    ant = antecedents[var_int]
    get_literals_from_clause(
      ant,
      current_dec_lvl,
      dec_lvls_of_vars,
      priority_queue,
      dec_lvl_set
    )
    
    # resolution
    assertive_clause.remove(lit_int)
    other_lit_int = lit_int ^ 1
    for lit_int in ant.children:
      if lit_int == other_lit_int:
        continue
      assertive_clause.add(lit_int)
      var_int = lit_int >> 1
      dec_lvl = dec_lvls_of_vars[var_int][0]
      if dec_lvl != current_dec_lvl and dec_lvl > highest_dec_lvl:
        highest_dec_lvl = dec_lvl
        highest_lit_int = lit_int

  satClause = SATClause(
    children=list(assertive_clause),
    lbd=sum(dec_lvl_set)
  )
  satClause._len = len(satClause.children)

  if len(satClause) == 1:
    satClause.watched = [0, None]
    highest_dec_lvl = 0
  else:
    w_1, w_2 = None, None
    dec_int = priority_queue[0][2]
    for i, c in enumerate(satClause.children):
      if c == highest_lit_int:
        w_1 = i
      elif c == dec_int:
        w_2 = i
    if w_1 is None:
      raise RuntimeError("Something went really wrong")
    satClause.watched = [w_1, w_2]

  return satClause, highest_dec_lvl
  

