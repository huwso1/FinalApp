class CFGGrammar:
    """
    Context-Free Grammar representation.
    """

    def __init__(self, variables=None, terminals=None, productions=None, start_symbol='S'):
        self.variables = set(variables or [])
        self.terminals = set(terminals or [])
        self.productions = {}  # Format: { 'S': ['AB', 'a'], ... }
        self.start_symbol = start_symbol

        if productions:
            self.parse_productions(productions)

    def parse_productions(self, lines):
        """
        Parses a list of production strings (e.g., "S -> A | b").
        """
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Handle both arrow types
            if '->' in line:
                lhs, rhs_block = line.split('->')
            elif '→' in line:
                lhs, rhs_block = line.split('→')
            else:
                continue

            lhs = lhs.strip()
            self.variables.add(lhs)
            
            # Split RHS alternatives by pipe
            alternatives = [alt.strip() for alt in rhs_block.split('|')]

            if lhs not in self.productions:
                self.productions[lhs] = []

            for alt in alternatives:
                # Handle epsilon/lambda explicitly or as empty string
                if alt in ['λ', 'ε', 'epsilon', '']:
                    clean_alt = 'λ'
                else:
                    clean_alt = alt
                    # Infer symbols
                    for char in clean_alt:
                        if char.isupper():
                            self.variables.add(char)
                        else:
                            self.terminals.add(char)
                
                self.productions[lhs].append(clean_alt)

        # Ensure start symbol is treated as a variable
        self.variables.add(self.start_symbol)

    def to_dict(self):
        """Returns a dictionary representation for the frontend."""
        return {
            "variables": sorted(list(self.variables)),
            "terminals": sorted(list(self.terminals)),
            "start": self.start_symbol,
            "productions": {k: v for k, v in self.productions.items()}
        }