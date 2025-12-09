class CFGGrammar:
    """
    Representación de una Gramática Libre de Contexto (GLC).

    Atributos:
        variables (set): Conjunto de símbolos no terminales de la gramática.
        terminals (set): Conjunto de símbolos terminales de la gramática.
        productions (dict): Diccionario que almacena las producciones.
            Formato: { 'S': ['AB', 'a'], ... }
        start_symbol (str): Símbolo inicial de la gramática.

    Métodos:
        __init__(variables, terminals, productions, start_symbol):
            Inicializa la gramática con variables, terminales, producciones y símbolo inicial.
        
        parse_productions(lines):
            Analiza una lista de cadenas que representan producciones (por ejemplo, "S -> A | b").
            Convierte las producciones en un formato interno y actualiza los conjuntos de
            variables y terminales.

        to_dict():
            Devuelve una representación en diccionario de la gramática, útil para
            su uso en la interfaz o frontend.
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
        Analiza una lista de cadenas de producción.

        Cada cadena debe tener el formato "LHS -> RHS1 | RHS2 | ...", donde:
            - LHS: símbolo no terminal del lado izquierdo.
            - RHS: alternativas del lado derecho separadas por '|'.
        
        La función:
            - Agrega símbolos a los conjuntos de variables y terminales.
            - Reconoce explícitamente epsilon/lambda ('λ', 'ε', 'epsilon', o cadena vacía)
              y lo normaliza como 'λ'.
        """
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Maneja ambos tipos de flechas
            if '->' in line:
                lhs, rhs_block = line.split('->')
            elif '→' in line:
                lhs, rhs_block = line.split('→')
            else:
                continue

            lhs = lhs.strip()
            self.variables.add(lhs)
            
            # Separa alternativas del RHS por '|'
            alternatives = [alt.strip() for alt in rhs_block.split('|')]

            if lhs not in self.productions:
                self.productions[lhs] = []

            for alt in alternatives:
                # Maneja epsilon/lambda explícitamente
                if alt in ['λ', 'ε', 'epsilon', '']:
                    clean_alt = 'λ'
                else:
                    clean_alt = alt
                    # Inferir símbolos
                    for char in clean_alt:
                        if char.isupper():
                            self.variables.add(char)
                        else:
                            self.terminals.add(char)
                
                self.productions[lhs].append(clean_alt)

        # Asegura que el símbolo inicial esté en el conjunto de variables
        self.variables.add(self.start_symbol)

    def to_dict(self):
        """
        Devuelve un diccionario con la representación de la gramática.

        Retorna:
            dict: {
                "variables": lista ordenada de símbolos no terminales,
                "terminals": lista ordenada de símbolos terminales,
                "start": símbolo inicial,
                "productions": diccionario de producciones
            }
        """
        return {
            "variables": sorted(list(self.variables)),
            "terminals": sorted(list(self.terminals)),
            "start": self.start_symbol,
            "productions": {k: v for k, v in self.productions.items()}
        }
