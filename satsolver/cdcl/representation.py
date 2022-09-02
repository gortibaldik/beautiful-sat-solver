import random
import satsolver.watched_literals.representation as wl_repre

from dataclasses import dataclass
from logzero import logger
from satsolver.utils.stats import SATSolverStats
from typing import List, Tuple

class SATClause(wl_repre.SATClause):
  def __init__(
    self,
    children: List[int],
    lbd: int
  ):
    super().__init__(children)
    self.lbd = lbd

@dataclass
class CDCLData:
  itv: List[str] = None
  itc: List[List[SATClause]] = None
  assignment: List[bool] = None
  antecedents: List[SATClause] = None
  dec_lvls_of_vars: List[Tuple[int, int]] = None
  current_dec_lvl: int = None
  c: List[SATClause] = None
  cs: List[SATClause] = None
  """Clauses that will undergo Unit Propagation in the next step"""
  
  stats: SATSolverStats = None
  conflict_limit: float = None
  lbd_limit: float = None
  n_variables: int = None
  assigned_literals: List[List[int]] = None
  def_dec_lvl: Tuple[int, int] = (-1, -1)
  learned_clauses: List[SATClause] = None
  luby_sequence: List[int] = None
  dec_vars: List[int] = None
  n_restarts: int = None
  k: int = None
  n_assigned_variables: int = None
  order_of_vars: List[int] = None

  def initialize(self):
    size_of_arrays = self.n_variables + 1
    self.decisions = [0] * size_of_arrays
    self.assigned_literals = [None] * size_of_arrays
    self.dec_vars = [None] * size_of_arrays
    self.antecedents = [None] * size_of_arrays
    self.dec_lvls_of_vars = [self.def_dec_lvl] * size_of_arrays
    self.cs = self.c
    self.current_dec_lvl = 0
    self.learned_clauses = []
    self.luby_sequence = [1]
    self.n_restarts = 0
    self.k = 1
    self.n_assigned_variables = 0
    self.generate_impl_itc()
    self.generate_new_order_of_vars()
    
  def generate_impl_itc(self):
    itc_impl = [0] * len(self.assignment)

    for c, _ in self.c:
      for i in c:
        itc_impl[i >> 1] += 1

    self.itc_impl = itc_impl
  
  def generate_impl_itlc(self):
    itlc_impl = []
    for i in self.itc_impl:
      itlc_impl.append(i)
    
    for c in self.learned_clauses:
      for i in c:
        itlc_impl[i >> 1] += 1
    
    self.itlc_impl = itlc_impl
  
  def generate_new_order_of_vars(self):
    self.generate_impl_itlc()
    self.order_of_vars = sorted(range(self.n_variables), key=lambda i: self.itlc_impl[i], reverse=True)

  def restart(self):
    self.decisions = ...

@dataclass
class CDCLConfig:
  debug: bool = False
  use_luby: bool = False
  use_restarts: bool = False
  base_unit: int = None