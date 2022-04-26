from logzero import logger

def pure_literal_elimination(vcm, removed_clauses, unit_assignment):
    assignment = {}
    while True:
        removed_values = set()
        for variable, clauses in vcm.items():
            if variable in unit_assignment:
                continue
            first_is_negative = None
            all_same, at_least_one = True, False
            for i, v in clauses:
                if i not in removed_clauses:
                    at_least_one = True
                    if first_is_negative is None:
                        first_is_negative = v
                    elif v != first_is_negative:
                        all_same = False
                        break

            all_same = all_same and at_least_one
            
            if all_same:
                assign_true = not first_is_negative
                logger.debug(f"{variable} = {assign_true}")
                assignment[variable] = assign_true
                removed_values.add(variable)
                for i, v in clauses:
                    removed_clauses.add(i)
        if len(removed_values) == 0:
            break

        for val in removed_values:
            vcm.pop(val)
    
    return assignment