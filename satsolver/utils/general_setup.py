import os

from argparse import ArgumentParser
from enum import Enum
from typing import List
from logzero import logger
from satsolver.task1 import tseitin_encoding
from satsolver.tseitin_encoding.ast_tree import ASTNaryNode, ASTUnaryNode, ASTVariableNode
from satsolver.tseitin_encoding.symbols import Symbols
from satsolver.tseitin_encoding.tseitin_transformation import log_node_info
from satsolver.utils.file_utils import read_from_input
from satsolver.utils.logging_utils import set_debug_level
from satsolver.utils.parser_utils import add_parser_debug_levels
from satsolver.utils.stats import SATSolverStats
from satsolver.utils.time import time_execution

class Extensions(Enum):
  DIMACS=".cnf"
  SMTLIB=".sat"

def recognize_file_extension(file_name: str):
  """
  Return Extensions Enum based on file_name (stdin (`file_name == None`) is treated as being in `.sat` format)
  """
  if file_name is None:
      return Extensions.DIMACS.value
  filename, file_extension = os.path.splitext(file_name)
  for extension in Extensions:
    if file_extension == extension.value:
      return extension
    
  raise RuntimeError("Invalid extension for input file: either DIMACS (.cnf) or SMTLIB (.sat)")

def create_variable_node(node_str: str):
  if node_str[0] == '-':
    var_node = ASTVariableNode(Symbols.VARIABLE, node_str[1:])
    node = ASTUnaryNode(Symbols.NOT)
    node.children = [var_node]
  elif node_str == "0":
    return None
  else:
    node = ASTVariableNode(Symbols.VARIABLE, node_str)
  return node

def read_dimacs(formula: str):
  conjunction = ASTNaryNode(Symbols.AND)
  for line in formula.split('\n'):
    if len(line) == 0:
      continue
    symbols = line.strip().split()
    if symbols[0] == "c":
      # comments with variable names
      continue

    if symbols[0] in ["0", "%"]:
      continue

    if symbols[0] == "p":
      if len(symbols) != 4:
        raise RuntimeError(f"Unexpected comment line: {line}")
      expected_vars = int(symbols[2])
      expected_clauses = int(symbols[3])
      continue

    if len(symbols) == 2:
      node = create_variable_node(symbols[0])
      conjunction.children.append(node)
      continue

    disjunction = ASTNaryNode(Symbols.OR)
    for symbol in symbols:
      node = create_variable_node(symbol)
      if node is not None:
        disjunction.children.append(node)
    conjunction.children.append(disjunction)
    
  log_node_info(conjunction)
  logger.info(f"EXPECTED: 'variables': {expected_vars}, 'subformulas': {expected_clauses}")
  return conjunction

def print_model(model, input_file, output_to_stdout):
  extension = recognize_file_extension(input_file)
  array_to_write = []
  if extension == Extensions.DIMACS:
    for variable, value in model.items():
      int_var = int(variable)
      if not value:
        int_var *= -1
      array_to_write.append(int_var)
    array_to_write = sorted(array_to_write, key=abs)
    for i in array_to_write:
      logger.info(i)
      if output_to_stdout:
        print(i)
  else:
    array_to_write = sorted(list(model.items()))
    for variable, value in array_to_write:
      if "__spec__" not in variable:
        logger.info(f"{variable}: {value}")
        if output_to_stdout:
          print(f"{variable}: {value}")

def print_result(result, model, stats: SATSolverStats, time, input_file, output_to_stdout):
  if result == "SAT":
    logger.warning(f"SAT; {stats} time: {time}")
    print_model(model, input_file, output_to_stdout)
  else:
    logger.warning(f"UNSAT; {stats}; time: {time}")

def pack_result_to_dict(
  *,
  result,
  model,
  stats: SATSolverStats,
  time
):
  return {
    "result": result,
    "model": model,
    "stats": stats,
    "time": time
  }

def read_tree(input_file: str, nnf_reduce_implications=True):
  """
  Read input in SMTLIB or DIMACS format (recognized by file extension) and create an abstract syntax tree.

  Args:

    @input_file: str
      - either None or .sat or .cnf format. None means the formula will be read from stdin and it is assumed the formula is in .cnf format.
      .sat format is transformed to tseitin encoding.
    
    @nnf_reduce_implications: bool
      - whether or not is the formula in the negation normal form. (Formulas in negation normal form are transformed to shorter tseitin encodings)
  """
  extension = recognize_file_extension(input_file)
  formula = read_from_input(input_file)
  if extension == Extensions.SMTLIB:
    return tseitin_encoding(formula, nnf_reduce_implications=nnf_reduce_implications)
  elif extension == Extensions.DIMACS:
    return read_dimacs(formula)

def get_info(
  *,
  name: str,
  taskName: str,
  benchmarkable: bool,
  symbol: str = None,
  options: List = [],
  argumentParser: ArgumentParser=None
):
  """Provides information needed by server/frontend for correctly displaying the benchmark in client browser
  
  Args:
    @name: (str)              name of the benchmark, cannot contain commas, nor ';'
    @taskName: (str)          name of the task
    @benchmarkable: (bool)    whether to display task in the benchmark/custom run menu (whether it can be ran on benchmarks)
    @symbol: (str)            symbol which to display in frontend
    @options: (List)          list of options for the algorithm run
  """
  if "," in name or ";" in name:
    raise RuntimeError(f"Commas ',' and ';' cannot be in the name of the algorithm! (name of the algorithm: {name})")
  
  if benchmarkable and symbol is None:
    raise RuntimeError(f"symbol cannot be None if benchmarkable")

  info = {
    "name": name,
    "taskName": taskName,
    "benchmarkable": benchmarkable,
    "symbol": symbol,
    "options": options
  }
  if argumentParser is not None:
    options_to_argparse(info, argumentParser)
  
  return info

from enum import Enum

class TypeOfOption(Enum):
  LIST  = "list"
  VALUE = "value"
  MULTILINE_VALUE = "multiline"
  CHECKBOX = "checkbox"

def create_option(
  name: str,
  type: TypeOfOption,
  default,
  hint: str = "",
  options: List = None
):
  if type != TypeOfOption.LIST and options is not None:
    raise RuntimeError(f"When not choosing {TypeOfOption.LIST}, options should be None (current options: {options})")
  if type == TypeOfOption.LIST and options is None:
    raise RuntimeError(f"When choosing {TypeOfOption.LIST}, options should not be None (current options: {options})")
  return {
    "name": name,
    "type": type.value,
    "default": default,
    "options": options,
    "hint": hint
  }

def options_to_argparse(info, argumentParser: ArgumentParser):
  options = info["options"]
  for option in options:
    name: str = option["name"]
    type = option["type"]
    default = option["default"]
    option_options = option["options"]
    hint = option["hint"]

    sanitized_name = "--" + name.replace(" ", "_")
    if type == "list":
      argumentParser.add_argument(sanitized_name, choices=option_options, default=default, help=hint)
    elif type == "checkbox":
      argumentParser.add_argument(sanitized_name, action=("store_true" if default == False else "store_false"), help=hint)
    elif type == "value":
      argumentParser.add_argument(sanitized_name, default=default, help=hint)

def find_model(
  satsolver_function,
  *,
  input_file=None,
  warning=False,
  debug=False,
  output_to_stdout=False,
  nnf_reduce_implications=True,
  **kwargs
):
  set_debug_level(warning=warning, debug=debug)
  ast_tree_root = read_tree(input_file, nnf_reduce_implications=nnf_reduce_implications)
  start, end, result, model, stats = time_execution(satsolver_function, ast_tree_root, debug, **kwargs)
  print_result(result, model, stats, end - start, input_file, output_to_stdout)
  return pack_result_to_dict(
    result=result,
    model=model,
    stats=stats,
    time=end - start
  )

def create_parser():
  parser = ArgumentParser()
  parser.add_argument("input_file", type=str, help="Input file in DIMACS (.cnf) or in SMTLIB (.sat) format.")
  parser.add_argument("--output_to_stdout", action="store_true")
  add_parser_debug_levels(parser)
  return parser
