import satsolver.cdcl.cdcl as cdcl_base_module

from logzero import logger
from satsolver.cdcl.decision_variable_selection import dec_var_selection_basic, dec_var_selection_static_sum
from satsolver.cdcl.representation import CDCLData, SATClause
from satsolver.decision_heuristics.decision_variable_selection import vsids_array_dec_var_selection, random_var_selection

def decay_after_conflict(data: CDCLData):
  if data.decay_step % data.decay_every_n_steps != 0:
    return
  for i in range(data.n_variables * 2):
    data.vsids_activity[i] *= data.vsids_decay

def bump_assertive_clause(data: CDCLData, assertive_clause: SATClause):
  for literal in assertive_clause.children:
    data.vsids_activity[literal] += 1

class CDCL(cdcl_base_module.CDCL):
  def heuristic_setup(
    self,
    dec_var_heuristic,
    data: CDCLData,
    vsids_decay:float=1.0,
    decay_every_n_steps:int=1,
    assumptions:str = ""
  ):
    vsids_decay = float(vsids_decay)
    assumptions = str(assumptions)
    if len(assumptions) > 0:
      data.assumptions = assumptions.split(".")
      for i in range(len(data.assumptions)):
        a = data.assumptions[i].strip()
        negative = False
        if "NOT" in a:
          a = a[3:].strip()
          negative = True
        for j, s in enumerate(data.itv):
          if a == s:
            data.assumptions[i] = j + j + negative
            break
        else:
          raise RuntimeError(f"{a} not found in data.itv ({data.itv})")

    if dec_var_heuristic == "No Heuristic":
      self.dec_var_selection = dec_var_selection_basic
    elif dec_var_heuristic == "Static Sum":
      self.dec_var_selection = dec_var_selection_static_sum
      self.use_static_heuristic = True
    elif dec_var_heuristic == "VSIDS_array":
      self.dec_var_selection = vsids_array_dec_var_selection
      data.vsids_activity = [0] * (data.n_variables * 2)
      if vsids_decay <= 0 or vsids_decay > 1:
        raise RuntimeError(f"vsids_decay should be in (0,1], current value: {vsids_decay}")
      data.vsids_decay = vsids_decay
      data.decay_every_n_steps = int(decay_every_n_steps)
      data.decay_step = 0
      self.conflict_found_callback = decay_after_conflict
      self.after_conflict_analysis_callback = bump_assertive_clause
    elif dec_var_heuristic == "Random":
      self.dec_var_selection = random_var_selection
    else:
      raise RuntimeError(f"Incorrect heuristic name ! ({dec_var_heuristic})")

