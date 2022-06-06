from logzero import logger
from satsolver.tseitin_encoding.symbols import Symbols
from satsolver.tseitin_encoding.ast_tree import ASTAbstractNode, ASTBinaryNode, ASTNaryNode, ASTUnaryNode, ASTVariableNode

def create_equivalence(subformula: ASTAbstractNode, additional_variable_index, equivalences):
    new_variable = ASTVariableNode(Symbols.VARIABLE, f"__spec__{additional_variable_index}")
    new_root = ASTBinaryNode(Symbols.EQUIVALENCE)

    if len(subformula.children) == 2:
        lc, rc = subformula.children
        for eq in equivalences:
            eq_node, node = eq.children
            if node == lc:
                subformula.children[0] = eq_node
            elif node == rc:
                subformula.children[1] = eq_node

    new_root.children = [ new_variable, subformula ]
    equivalences.append(new_root)
    return new_root

def equivalence_to_implications(equivalence_formula: ASTAbstractNode, nnf_reduce_implications: bool):
    special_variable, subformula = equivalence_formula.children

    and_root = ASTBinaryNode(Symbols.AND)
    impl1_subroot = ASTBinaryNode(Symbols.IMPLICATION)
    impl2_subroot = ASTBinaryNode(Symbols.IMPLICATION)

    impl1_subroot.children = [special_variable, subformula]

    if nnf_reduce_implications:
        return impl1_subroot

    impl2_subroot.children = [subformula, special_variable]

    and_root.children = [ impl1_subroot, impl2_subroot]
    return and_root

def negate_literal(formula: ASTAbstractNode):
    if formula.type == Symbols.VARIABLE:
        not_formula = ASTUnaryNode(Symbols.NOT)
        not_formula.children = [ formula ]
    elif formula.type == Symbols.NOT:
        not_formula: ASTVariableNode = formula.children[0]
    return not_formula

def negate_and(formula: ASTAbstractNode):
    """not (a and b) ~~ not a or not b"""
    a, b = formula.children
    not_a = negate(a)
    not_b = negate(b)
    
    or_node = ASTBinaryNode(Symbols.OR)
    or_node.children = [ not_a, not_b ]
    return or_node

def negate_or(formula: ASTAbstractNode):
    """not (a or b) ~~ not a and not b"""
    a, b = formula.children
    not_a = negate(a)
    not_b = negate(b)

    and_node = ASTBinaryNode(Symbols.AND)
    and_node.children = [ not_a, not_b ]
    return and_node

def negate(formula: ASTAbstractNode):
    if len(formula.children) <= 1:
        return negate_literal(formula)
    if formula.type == Symbols.AND:
        return negate_and(formula)
    if formula.type == Symbols.OR:
        return negate_or(formula)
    
    raise RuntimeError(f"negate({formula})")

def merge_or(*args):
    result = ASTNaryNode(Symbols.OR)
    for sf in args:
        if sf.type == Symbols.OR:
            result.children += sf.children
        elif len(sf.children) <= 1:
            result.children.append(sf)
        else:
            raise RuntimeError(f"merge_or: {sf}")
    return result

def merge_and(*args):
    result = ASTNaryNode(Symbols.AND)
    and_children = []
    for c in args:
        if c.type == Symbols.AND:
            and_children += c.children
        else:
            and_children.append(c)
    result.children = and_children
    return result

def multiply_or(a_and_b: ASTAbstractNode, c: ASTAbstractNode):
    """(a and b) or c ~~ (a or c) and (b or c)"""
    a, b = a_and_b.children
    a_or_c = ASTBinaryNode(Symbols.OR)
    a_or_c.children = [a, c]

    b_or_c = ASTBinaryNode(Symbols.OR)
    b_or_c.children = [b, c]

    a_or_c_and_b_or_c = ASTBinaryNode(Symbols.AND)
    a_or_c_and_b_or_c.children = [a_or_c, b_or_c]

    return a_or_c_and_b_or_c

def or_to_sat(formula: ASTAbstractNode):
    """
    ((a or b) or c)  ~~ (a or b or c)
    ((a and b) or c) ~~ ((a or c) and (b or c))
    """
    if formula.type != Symbols.OR:
        raise RuntimeError(f"or_to_sat({formula})")

    left_child, right_child = formula.children
    if left_child.type == Symbols.OR or right_child.type == Symbols.OR:
        return merge_or(left_child, right_child)

    if left_child.type == Symbols.AND:
        return multiply_or(left_child, right_child)
    if right_child.type == Symbols.AND:
        return multiply_or(right_child, left_child)
    
    return formula

def implication_to_sat(implication_formula: ASTAbstractNode):
    """
    (a and b) -> c ~~ ((not a or not b) or not_c) ~~ (not_a or not_b or not_c)          -- merge_or
    (a or b)  -> c ~~ ((not a and not b) or c)    ~~ ((not_a or c) and (not_b or c))    -- multiply_or
    not a     -> c ~~ (a or c)
    a         -> c ~~ (not a or c)
    
    c -> (a and b) ~~ (not c or (a and b)) ~~ ((not c or a) and (not c or b))           --multiply_or
    c -> (a or b)  ~~ (not c or (a or b))  ~~ (not c or a or b)                         -- merge or
    c -> not a     ~~ (not c or not a)
    c -> a         ~~ (not c or a)
    """
    if implication_formula.type != Symbols.IMPLICATION:
        print("implication: ")
        print(implication_formula)
        print()
        raise RuntimeError("Not valid implication forula")
    
    lc, rc = implication_formula.children
    not_lc = negate(lc)

    or_node = ASTBinaryNode(Symbols.OR)
    or_node.children = [not_lc, rc]
    or_sat_node = or_to_sat(or_node)

    return or_sat_node

def implications_to_sat(and_formula: ASTAbstractNode, nnf_reduce_implications: bool):
    if nnf_reduce_implications:
        return implication_to_sat(and_formula)

    if and_formula.type != Symbols.AND:
        print("base formula:")
        and_formula.print()
        print()
        raise RuntimeError("Not valid formula!")

    lc, rc = and_formula.children
    lc = implication_to_sat(lc)
    rc = implication_to_sat(rc)
    
    return merge_and(lc, rc)

def log_node_info(node: ASTAbstractNode):
    logger.info(node)
    cnt = node.count()
    cnt["variables"] = len(cnt["variables"])
    logger.info(cnt)

def turn_nnf_to_tseitin(root_of_nnf: ASTAbstractNode, nnf_reduce_implications: bool):
    log_node_info(root_of_nnf)
    sfs = root_of_nnf.get_subformulas()
    sfs.reverse()

    # in equivalences spec_i <-> subformula
    # is held, so that spec_i is substituted for
    # subformula in each subsequent subformula
    equivalences = []
    top_level_and = ASTNaryNode(Symbols.AND)
    for i, sf in enumerate(sfs):
        logger.debug("----")
        logger.debug(sf)

        eq = create_equivalence(sf, i, equivalences)
        logger.debug(eq)

        imp = equivalence_to_implications(eq, nnf_reduce_implications)
        logger.debug(imp)

        imp = implications_to_sat(imp, nnf_reduce_implications)
        logger.debug(imp)

        top_level_and = merge_and(*top_level_and.children, imp)
    
    top_level_and.children = [equivalences[-1].children[0]] + top_level_and.children

    log_node_info(top_level_and)
    return top_level_and