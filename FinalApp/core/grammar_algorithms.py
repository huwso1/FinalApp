class GrammarAlgorithms:
    """
    Implements standard CFG algorithms.
    """

    def __init__(self, grammar):
        self.g = grammar

    def compute_terminating_variables(self):
        """
        Returns set of variables that can eventually derive a string of terminals.
        (Also known as 'Generating' variables).
        """
        generating = set()
        
        # 1. Identify variables yielding strings of terminals immediately
        # (or variables deriving epsilon)
        for lhs, rhs_list in self.g.productions.items():
            for rhs in rhs_list:
                if rhs == 'λ' or all(s in self.g.terminals for s in rhs):
                    generating.add(lhs)

        # 2. Iteratively add variables
        changed = True
        while changed:
            changed = False
            for lhs, rhs_list in self.g.productions.items():
                if lhs in generating:
                    continue
                
                for rhs in rhs_list:
                    # If all symbols in RHS are either terminals or already generating
                    if rhs != 'λ' and all(s in self.g.terminals or s in generating for s in rhs):
                        generating.add(lhs)
                        changed = True
                        break  # No need to check other alternatives for this var
        
        return generating

    def compute_reachable_variables(self, grammar_instance=None):
        """
        Returns set of variables reachable from the Start Symbol.
        Can optionally accept a specific grammar instance (useful for pipelining).
        """
        grammar = grammar_instance if grammar_instance else self.g
        
        reachable = {grammar.start_symbol}
        to_process = [grammar.start_symbol]
        
        while to_process:
            current = to_process.pop()
            
            if current in grammar.productions:
                for rhs in grammar.productions[current]:
                    if rhs == 'λ': continue
                    for symbol in rhs:
                        if symbol in grammar.variables and symbol not in reachable:
                            reachable.add(symbol)
                            to_process.append(symbol)
        
        return reachable

    def compute_nullable_variables(self):
        """
        Returns set of variables that can derive epsilon (λ).
        """
        nullable = set()

        # 1. Direct epsilon productions
        for lhs, rhs_list in self.g.productions.items():
            if 'λ' in rhs_list:
                nullable.add(lhs)

        # 2. Iterative discovery
        changed = True
        while changed:
            changed = False
            for lhs, rhs_list in self.g.productions.items():
                if lhs in nullable:
                    continue
                
                for rhs in rhs_list:
                    if rhs == 'λ': continue
                    # If all symbols in RHS are nullable
                    if all(s in nullable for s in rhs):
                        nullable.add(lhs)
                        changed = True
                        break
        return nullable

    def compute_unit_closure(self, variable):
        """
        Returns set of variables reachable from 'variable' via unit productions (A -> B).
        """
        closure = {variable}
        changed = True
        while changed:
            changed = False
            current_set = list(closure)
            for v in current_set:
                if v in self.g.productions:
                    for rhs in self.g.productions[v]:
                        # Check if RHS is a single variable
                        if len(rhs) == 1 and rhs in self.g.variables:
                            if rhs not in closure:
                                closure.add(rhs)
                                changed = True
        return closure

    def eliminate_useless_variables(self):
        """
        Step 1: Eliminate Non-Generating (Non-Terminating) variables.
        Step 2: Eliminate Unreachable variables.
        Returns a NEW CFGGrammar object.
        """
        from core.cfg_grammar import CFGGrammar

        # --- STEP 1: REMOVE NON-GENERATING ---
        generating = self.compute_terminating_variables()
        
        # Filter productions: keep only those where all variables are generating
        step1_productions = {}
        for lhs in generating:
            if lhs not in self.g.productions: continue
            
            valid_rhs_list = []
            for rhs in self.g.productions[lhs]:
                if rhs == 'λ':
                    valid_rhs_list.append(rhs)
                    continue
                
                # Check if every variable in RHS is generating
                is_valid = True
                for char in rhs:
                    if char in self.g.variables and char not in generating:
                        is_valid = False
                        break
                if is_valid:
                    valid_rhs_list.append(rhs)
            
            if valid_rhs_list:
                step1_productions[lhs] = valid_rhs_list

        # If start symbol is not generating, grammar is empty
        if self.g.start_symbol not in generating:
            return CFGGrammar(variables=[], terminals=[], productions=[], start_symbol=self.g.start_symbol)

        # Create intermediate grammar
        temp_grammar = CFGGrammar(
            variables=list(generating),
            terminals=list(self.g.terminals),
            start_symbol=self.g.start_symbol
        )
        temp_grammar.productions = step1_productions

        # --- STEP 2: REMOVE UNREACHABLE ---
        # Note: We run reachability on the temp_grammar, not self.g
        reachable = self.compute_reachable_variables(grammar_instance=temp_grammar)
        
        final_productions = []
        final_vars = set()

        for lhs in reachable:
            if lhs in temp_grammar.productions:
                rhss = temp_grammar.productions[lhs]
                # Re-format for the constructor
                if rhss:
                    line = f"{lhs} -> {' | '.join(rhss)}"
                    final_productions.append(line)
                    final_vars.add(lhs)
        
        # Terminals might have been reduced too, strictly speaking, 
        # but keeping the original set is usually harmless. 
        # We can re-infer them if we want perfection.
        
        return CFGGrammar(
            variables=list(final_vars),
            terminals=list(self.g.terminals),
            productions=final_productions,
            start_symbol=self.g.start_symbol
        )