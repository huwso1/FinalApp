class GrammarAlgorithms:
    """
    Implementa algoritmos estándar para Gramáticas Libres de Contexto (GLC).

    Atributos:
        g (CFGGrammar): Instancia de la gramática sobre la cual se aplican los algoritmos.

    Métodos:
        __init__(grammar):
            Inicializa la clase con una instancia de CFGGrammar.
        
        compute_terminating_variables():
            Devuelve el conjunto de variables que eventualmente pueden derivar en
            una cadena de terminales (también conocidas como variables generadoras).
            Retorna además los pasos detallados del proceso.
        
        compute_reachable_variables(grammar_instance=None):
            Devuelve el conjunto de variables alcanzables desde el símbolo inicial.
            Puede recibir una instancia de gramática específica para procesar.
            Retorna también los pasos detallados del cálculo.
        
        compute_nullable_variables():
            Devuelve el conjunto de variables que pueden derivar epsilon (λ).
            Incluye los pasos iterativos del cálculo.
        
        compute_unit_closure(variable):
            Devuelve el conjunto de variables alcanzables desde 'variable' a través
            de producciones unitarias (A → B).
        
        eliminate_useless_variables():
            Elimina variables inútiles en dos pasos:
                1. Variables no generadoras (no terminables).
                2. Variables inalcanzables desde el símbolo inicial.
            Devuelve un nuevo objeto CFGGrammar simplificado y los pasos detallados.
    """

    def __init__(self, grammar):
        self.g = grammar

    def compute_terminating_variables(self):
        """
        Calcula las variables terminables (generadoras).

        Retorna:
            generating (set): Conjunto de variables que pueden derivar cadenas de terminales.
            steps (list): Lista de pasos iterativos detallando el cálculo.
        """
        steps = []
        generating = set()
        
        # 1. Identificar variables que producen directamente cadenas de terminales
        step1_vars = set()
        for lhs, rhs_list in self.g.productions.items():
            for rhs in rhs_list:
                if rhs == 'λ' or all(s in self.g.terminals for s in rhs):
                    generating.add(lhs)
                    step1_vars.add(lhs)
        
        steps.append({
            "iteration": "TERM_2",
            "variables": f"{{{', '.join(sorted(step1_vars))}}}" if step1_vars else "∅",
            "explanation": "Variables con producción directa a terminales",
            "newVariables": sorted(list(step1_vars))
        })
        
        # 2. Iteración para añadir variables generadoras indirectas
        iteration = 2
        changed = True
        while changed:
            changed = False
            new_vars = set()
            
            for lhs, rhs_list in self.g.productions.items():
                if lhs in generating:
                    continue
                
                for rhs in rhs_list:
                    if rhs == 'λ':
                        continue
                    if all(s in self.g.terminals or s in generating for s in rhs):
                        generating.add(lhs)
                        new_vars.add(lhs)
                        changed = True
                        break
            
            if new_vars:
                steps.append({
                    "iteration": f"TERM_{iteration}",
                    "variables": f"{{{', '.join(sorted(generating))}}}",
                    "explanation": f"Variables con RHS en (Σ ∪ TERM_{iteration-1})*",
                    "newVariables": sorted(list(new_vars))
                })
                iteration += 1
        
        steps.append({
            "iteration": "Resultado Final",
            "variables": f"{{{', '.join(sorted(generating))}}}",
            "explanation": "Conjunto TERM de variables terminables",
            "type": "terminating"
        })
        
        return generating, steps

    def compute_reachable_variables(self, grammar_instance=None):
        """
        Calcula las variables alcanzables desde el símbolo inicial.

        Args:
            grammar_instance (CFGGrammar, opcional): Instancia específica de gramática.

        Retorna:
            reachable (set): Conjunto de variables alcanzables.
            steps (list): Lista de pasos iterativos detallando el cálculo.
        """
        grammar = grammar_instance if grammar_instance else self.g
        steps = []
        reachable = {grammar.start_symbol}
        
        steps.append({
            "iteration": "ALC₁",
            "variables": f"{{{grammar.start_symbol}}}",
            "explanation": "Símbolo inicial",
            "newVariables": [grammar.start_symbol],
            "type": "reachable"
        })
        
        iteration = 2
        changed = True
        while changed:
            changed = False
            new_vars = set()
            current_reachable = list(reachable)
            
            for current in current_reachable:
                if current in grammar.productions:
                    for rhs in grammar.productions[current]:
                        if rhs == 'λ': 
                            continue
                        for symbol in rhs:
                            if symbol in grammar.variables and symbol not in reachable:
                                reachable.add(symbol)
                                new_vars.add(symbol)
                                changed = True
            
            if new_vars:
                steps.append({
                    "iteration": f"ALC_{iteration}",
                    "variables": f"{{{', '.join(sorted(reachable))}}}",
                    "explanation": "Variables en producciones de variables alcanzables",
                    "newVariables": sorted(list(new_vars)),
                    "type": "reachable"
                })
                iteration += 1
        
        steps.append({
            "iteration": "Resultado Final",
            "variables": f"{{{', '.join(sorted(reachable))}}}",
            "explanation": "Conjunto ALC de variables alcanzables",
            "type": "reachable"
        })
        
        return reachable, steps

    def compute_nullable_variables(self):
        """
        Calcula las variables anulables (que pueden derivar λ).

        Retorna:
            nullable (set): Conjunto de variables anulables.
            steps (list): Lista de pasos iterativos detallando el cálculo.
        """
        steps = []
        nullable = set()

        # 1. Producciones directas a λ
        step1_vars = set()
        for lhs, rhs_list in self.g.productions.items():
            if 'λ' in rhs_list:
                nullable.add(lhs)
                step1_vars.add(lhs)
        
        steps.append({
            "iteration": "ANUL₁",
            "variables": f"{{{', '.join(sorted(step1_vars))}}}" if step1_vars else "∅",
            "explanation": "Variables con producción A → λ",
            "newVariables": sorted(list(step1_vars)),
            "type": "nullable"
        })
        
        # 2. Descubrimiento iterativo de variables anulables indirectas
        iteration = 2
        changed = True
        while changed:
            changed = False
            new_vars = set()
            
            for lhs, rhs_list in self.g.productions.items():
                if lhs in nullable:
                    continue
                
                for rhs in rhs_list:
                    if rhs == 'λ': 
                        continue
                    if all(s in nullable for s in rhs):
                        nullable.add(lhs)
                        new_vars.add(lhs)
                        changed = True
                        break
            
            if new_vars:
                steps.append({
                    "iteration": f"ANUL_{iteration}",
                    "variables": f"{{{', '.join(sorted(nullable))}}}",
                    "explanation": f"Variables con producción A → w, w ∈ (ANUL_{iteration-1})*",
                    "newVariables": sorted(list(new_vars)),
                    "type": "nullable"
                })
                iteration += 1
        
        steps.append({
            "iteration": "Resultado Final",
            "variables": f"{{{', '.join(sorted(nullable))}}}",
            "explanation": "Conjunto ANUL de variables anulables",
            "type": "nullable"
        })
        
        return nullable, steps

    def compute_unit_closure(self, variable):
        """
        Calcula el cierre unitario de una variable.

        Args:
            variable (str): Variable de inicio.

        Retorna:
            closure (set): Conjunto de variables alcanzables mediante producciones unitarias (A → B).
        """
        closure = {variable}
        changed = True
        while changed:
            changed = False
            current_set = list(closure)
            for v in current_set:
                if v in self.g.productions:
                    for rhs in self.g.productions[v]:
                        if len(rhs) == 1 and rhs in self.g.variables:
                            if rhs not in closure:
                                closure.add(rhs)
                                changed = True
        return closure

    def eliminate_useless_variables(self):
        """
        Elimina variables inútiles de la gramática en dos pasos:

        1. Eliminación de variables no generadoras (no terminables).
        2. Eliminación de variables inalcanzables desde el símbolo inicial.

        Retorna:
            new_grammar (CFGGrammar): Nueva gramática simplificada.
            steps (list): Lista de pasos detallando la eliminación de variables.
        """
        from cfg_grammar import CFGGrammar
        steps = []

        steps.append({
            "iteration": "Inicio",
            "variables": "Gramática original",
            "explanation": "Inicio del proceso de eliminación",
            "type": "useless"
        })

        # Paso 1: eliminar variables no generadoras
        generating, gen_steps = self.compute_terminating_variables()
        for step in gen_steps[:-1]:
            steps.append({
                "iteration": f"Gen: {step['iteration']}",
                "variables": step['variables'],
                "explanation": step['explanation'],
                "type": "terminating"
            })
        
        steps.append({
            "iteration": "Paso 1",
            "variables": f"TERM = {{{', '.join(sorted(generating))}}}",
            "explanation": f"Variables terminables encontradas: {len(generating)} variables",
            "type": "useless"
        })

        # Filtrar producciones según variables generadoras
        step1_productions = {}
        removed_vars_step1 = []
        for lhs in generating:
            if lhs not in self.g.productions: 
                continue
            
            valid_rhs_list = []
            for rhs in self.g.productions[lhs]:
                if rhs == 'λ':
                    valid_rhs_list.append(rhs)
                    continue
                
                is_valid = True
                for char in rhs:
                    if char in self.g.variables and char not in generating:
                        is_valid = False
                        break
                if is_valid:
                    valid_rhs_list.append(rhs)
            
            if valid_rhs_list:
                step1_productions[lhs] = valid_rhs_list
        
        all_vars = set(self.g.variables)
        removed_vars_step1 = sorted(list(all_vars - generating))
        
        if removed_vars_step1:
            steps.append({
                "iteration": "Eliminación",
                "variables": f"Variables no generadoras: {{{', '.join(removed_vars_step1)}}}",
                "explanation": "Eliminadas en Paso 1 (no terminables)",
                "type": "useless"
            })
        else:
            steps.append({
                "iteration": "Eliminación",
                "variables": "No se eliminaron variables",
                "explanation": "Todas las variables son terminables",
                "type": "useless"
            })

        if self.g.start_symbol not in generating:
            steps.append({
                "iteration": "Resultado",
                "variables": "Gramática vacía",
                "explanation": "El símbolo inicial no es terminable",
                "type": "useless"
            })
            return CFGGrammar(variables=[], terminals=[], productions=[], start_symbol=self.g.start_symbol), steps

        temp_grammar = CFGGrammar(
            variables=list(generating),
            terminals=list(self.g.terminals),
            start_symbol=self.g.start_symbol
        )
        temp_grammar.productions = step1_productions

        # Paso 2: eliminar variables inalcanzables
        reachable, reach_steps = self.compute_reachable_variables(grammar_instance=temp_grammar)
        for step in reach_steps[:-1]:
            steps.append({
                "iteration": f"Alc: {step['iteration']}",
                "variables": step['variables'],
                "explanation": step['explanation'],
                "type": "reachable"
            })
        
        steps.append({
            "iteration": "Paso 2",
            "variables": f"ALC = {{{', '.join(sorted(reachable))}}}",
            "explanation": f"Variables alcanzables encontradas: {len(reachable)} variables",
            "type": "useless"
        })

        final_productions = []
        final_vars = set()
        removed_vars_step2 = sorted(list(set(temp_grammar.variables) - reachable))

        for lhs in reachable:
            if lhs in temp_grammar.productions:
                rhss = temp_grammar.productions[lhs]
                if rhss:
                    line = f"{lhs} -> {' | '.join(rhss)}"
                    final_productions.append(line)
                    final_vars.add(lhs)
        
        if removed_vars_step2:
            steps.append({
                "iteration": "Eliminación",
                "variables": f"Variables inalcanzables: {{{', '.join(removed_vars_step2)}}}",
                "explanation": "Eliminadas en Paso 2 (no alcanzables desde S)",
                "type": "useless"
            })
        else:
            steps.append({
                "iteration": "Eliminación",
                "variables": "No se eliminaron variables",
                "explanation": "Todas las variables son alcanzables",
                "type": "useless"
            })

        steps.append({
            "iteration": "Resultado Final",
            "variables": f"Gramática simplificada con {len(final_vars)} variables",
            "explanation": f"Producciones: {len(final_productions)}",
            "type": "useless"
        })
        
        return CFGGrammar(
            variables=list(final_vars),
            terminals=list(self.g.terminals),
            productions=final_productions,
            start_symbol=self.g.start_symbol
        ), steps
