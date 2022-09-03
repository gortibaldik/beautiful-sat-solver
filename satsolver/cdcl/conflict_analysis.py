from heapq import heappop, heappush
from logzero import logger
from satsolver.utils.representation import debug_str_multi
from satsolver.cdcl.representation import CDCLData, SATClause

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
  for lit_int in clause.children:
    var_int = lit_int >> 1
    tpl = dec_lvls_of_vars[var_int]
    if tpl[0] == current_dec_lvl:
      if tpl[1] <= 0:
        heappush(priority_queue, (*tpl, lit_int))

        # prevents the dec var to be traversed multiple
        # times
        dec_lvls_of_vars[var_int] = (tpl[0], 1)

  return priority_queue, highest_dec_lvl, highest_lit_int

def get_literals_from_clause(
  clause: SATClause,
  current_dec_lvl,
  dec_lvls_of_vars,
  priority_queue
):
  should_collect_dec_lvl_set = isinstance(clause, SATClause)
  if should_collect_dec_lvl_set:
    clause_dec_lvl_set = [False] * (current_dec_lvl + 1)
  for lit_int in clause.children:
    var_int = lit_int >> 1
    tpl = dec_lvls_of_vars[var_int]
    if tpl[0] == current_dec_lvl:
      if tpl[1] <= 0:
        heappush(priority_queue, (*tpl, lit_int))

        # prevents the dec var to be traversed multiple
        # times
        dec_lvls_of_vars[var_int] = (tpl[0], 1)
      if should_collect_dec_lvl_set and not clause_dec_lvl_set[tpl[0]]:
        clause_dec_lvl_set[tpl[0]] = True
    elif should_collect_dec_lvl_set:
      clause_dec_lvl_set[tpl[0]] = True

  if should_collect_dec_lvl_set:
    clause.lbd = sum(clause_dec_lvl_set)

def conflict_analysis(conflict_clause: SATClause, data: CDCLData):
  priority_queue, highest_dec_lvl, highest_lit_int = init_literals_from_clause(
    conflict_clause,
    data.current_dec_lvl,
    data.itv,
    data.dec_lvls_of_vars
  )
  assertive_clause = set(conflict_clause.children)

  # stop at the first UIP
  # hence when len(deq) <= 1
  assignment_order = []
  while len(priority_queue) > 1:
    _, _, lit_int = heappop(priority_queue)
    var_int = lit_int >> 1

    ant = data.antecedents[var_int]
    get_literals_from_clause(
      ant,
      data.current_dec_lvl,
      data.dec_lvls_of_vars,
      priority_queue
    )
    if len(priority_queue) <= 1:
      tpl = priority_queue[0]
      heappush(assignment_order, (- tpl[0], tpl[1], tpl[2]))
    
    # resolution
    assertive_clause.remove(lit_int)
    other_lit_int = lit_int ^ 1
    for lit_int in ant.children:
      if lit_int == other_lit_int:
        continue
      assertive_clause.add(lit_int)
      var_int = lit_int >> 1
      dec_lvl = data.dec_lvls_of_vars[var_int][0]
      if dec_lvl != data.current_dec_lvl:
        tpl = data.dec_lvls_of_vars[var_int]
        heappush(assignment_order, (-tpl[0], tpl[1], lit_int))
  
  # traverse all the remaining antecedents
  # only to update lbd
  if len(priority_queue) > 0:
    dec_int = priority_queue[0][2]

  while len(priority_queue) > 0:
    _, _, lit_int = heappop(priority_queue)
    var_int = lit_int >> 1
    ant = data.antecedents[var_int]
    if ant is None:
      break
    get_literals_from_clause(
      ant,
      data.current_dec_lvl,
      data.dec_lvls_of_vars,
      priority_queue
    )
  
  # subsumption
  removed = [False] * data.n_variables
  for _ in range(len(assignment_order)):
    _, _, lit_int = heappop(assignment_order)
    var_int = lit_int >> 1
    if removed[var_int]:
      continue
    removed[var_int] = True
    ant = data.antecedents[var_int]
    if ant is None:
      continue
    
    # resolution
    is_subsumed = True
    other_lit_int = lit_int ^ 1
    for ant_lit_int in ant.children:
      if ant_lit_int == other_lit_int:
        continue
      if ant_lit_int not in assertive_clause:
        is_subsumed = False
        break
    if is_subsumed:
      assertive_clause.remove(lit_int)
  
  dec_lvl_set = [False] * (data.current_dec_lvl + 1)
  assertive_clause = list(assertive_clause)
  for lit_int in assertive_clause:
    dec_lvl, _ = data.dec_lvls_of_vars[lit_int >> 1]
    if not dec_lvl_set[dec_lvl]:
      dec_lvl_set[dec_lvl] = True
      if dec_lvl > highest_dec_lvl and dec_lvl != data.current_dec_lvl:
        highest_dec_lvl = dec_lvl
        highest_lit_int = lit_int

  satClause = SATClause(
    children=assertive_clause,
    lbd=sum(dec_lvl_set)
  )
  satClause._len = len(satClause.children)

  if len(satClause) == 1:
    satClause.watched = [0, None]
    highest_dec_lvl = 0
  else:
    w_1, w_2 = None, None
    for i, c in enumerate(satClause.children):
      if c == highest_lit_int:
        w_1 = i
      elif c == dec_int:
        w_2 = i
    if w_1 is None:
      raise RuntimeError("Something went really wrong")
    satClause.watched = [w_1, w_2]

  return satClause, highest_dec_lvl
