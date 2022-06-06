from logzero import logger
from satsolver.tseitin_encoding.ast_tree import ASTAbstractNode

def _update_mapping(vcm, clause_index, value, negative: bool):
    vcm[value] = vcm.get(value, []) + [(clause_index, negative)]


def update_mapping(*, vcm, clause_index, child):
    if len(child.children) == 0:
        _update_mapping(vcm, clause_index, child._value, negative=False)
    elif len(child.children) == 1:
        _update_mapping(vcm, clause_index, child.children[0]._value, negative=True)

def create_clause_mapping(ast_tree_root: ASTAbstractNode):
    vcm = {} # variable clauses mapping
    unit_clauses = set()
    for i, c in enumerate(ast_tree_root.children):
        if len(c.children) <= 1:
            update_mapping(vcm=vcm, clause_index=i, child=c)
            unit_clauses.add(c)
        else:
            for sub_c in c.children:
                update_mapping(vcm=vcm, clause_index=i, child=sub_c)
    return vcm, unit_clauses

def find_clause_child(clause, value):
    for i, c in enumerate(clause.children):
        if len(c.children) == 0:
            if c._value == value:
                return i
        elif len(c.children) == 1:
            if c.children[0]._value == value:
                return i
    
    raise RuntimeError(f"INVALID REMOVAL of {value} from {clause}")


def set_unit_clause_assignment(unit_clause: ASTAbstractNode, assignment):
    # the clause is unit, therefore
    # either it is just a variable node
    # or it is a not node with only one child
    not_node = len(unit_clause.children) == 1
    var_name = unit_clause.children[0]._value if not_node else unit_clause._value
    assignment[var_name] = not not_node
    return not not_node, var_name


def unit_propagation(ast_tree_root: ASTAbstractNode):
    # vcm - variable clause mapping
    # each variable is mapped to a list of clauses it appears in
    vcm, unit_clauses = create_clause_mapping(ast_tree_root)
    assignment = {}
    removed_clauses = set()

    while len(unit_clauses) != 0:
        first = unit_clauses.pop()
        assigned_value, var_name = set_unit_clause_assignment(first, assignment)
        logger.debug(f"-- UNIT PROPAGATION: {first}")

        # clause index and info whether variable is present in the
        # clause as negative literal
        remove_from_vcmvar_name = set()
        for i, (clause_index, clause_negative) in enumerate(vcm[var_name]):
            if clause_index not in removed_clauses:
                remove_from_vcmvar_name.add(i)

                # if literal is in the clause, remove clause
                if clause_negative == (not assigned_value):
                    logger.debug(f"REMOVE {ast_tree_root.children[clause_index]}")
                    removed_clauses.add(clause_index)
                else:
                    clause = ast_tree_root.children[clause_index]
                    if len(clause.children) <= 1:
                        # unit propagation found contradiction
                        return None, None, None

                    logger.debug(f"DECREASE: {clause} || {var_name}")
                    idx_to_remove = find_clause_child(clause, var_name)
                    clause.children.pop(idx_to_remove)
                    if len(clause.children) == 1:
                        # found another unit clause!
                        remaining_child = clause.children[0]
                        logger.debug(f"NEW UNIT: {remaining_child}")
                        ast_tree_root.children[clause_index] = remaining_child
                        unit_clauses.add(remaining_child)
        for i in sorted(remove_from_vcmvar_name, reverse=True):
            vcm[var_name].pop(i)

    return assignment, vcm, removed_clauses