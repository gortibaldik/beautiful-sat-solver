from pysat.solvers import Glucose4, Minisat22, Lingeling, Cadical, Solver
from satsolver.utils.enums import SATSolverResult
from satsolver.utils.stats import SATSolverStats
from satsolver.wrappers.prepare_structures import prepare_structures

GLUCOSE_SOLVER = "Glucose"
MINISAT = "Minisat"
LINGELING = "Lingeling"
CADICAL = "Cadical"

case_dict = {
  GLUCOSE_SOLVER: Glucose4,
  MINISAT: Minisat22,
  LINGELING: Lingeling,
  CADICAL: Cadical
}

def create_solver(solver_name: str):
  if solver_name is None or solver_name not in case_dict:
    raise RuntimeError(f"Invalid solver name: ({solver_name})")
  s_constr = case_dict[solver_name]
  solver: Solver = s_constr()
  return solver

def solve(
  ast_tree_root,
  debug,
  solver_name=None
):
  with create_solver(solver_name) as solver:
    vti = prepare_structures(ast_tree_root, solver)
    result = solver.solve()
    assignment = solver.get_model()
    stats = solver.accum_stats()
    stats = SATSolverStats(
      unitProps=stats["propagations"],
      decVars=stats["decisions"],
      conflicts=stats["conflicts"]
    )
    result = SATSolverResult.SAT if result else SATSolverResult.UNSAT
  
  model = None
  if result == SATSolverResult.SAT:
    model = {}
    for var_name, var_int in vti.items():
      var_int += 1
      model[var_name] = var_int in assignment
  
  return result.value, model, stats
