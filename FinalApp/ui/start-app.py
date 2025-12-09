import webview
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
sys.path.append(PROJECT_ROOT)

from core.cfg_grammar import CFGGrammar
from core.grammar_algorithms import GrammarAlgorithms

class AppAPI:
    def __init__(self):
        self.grammar = None
        self.alg = None

    def load_grammar(self, productions_text):
        """Parses grammar from frontend input."""
        try:
            lines = [ln.strip() for ln in productions_text.split("\n") if ln.strip()]
            if not lines:
                raise ValueError("No hay ninguna regla.")

            self.grammar = CFGGrammar(productions=lines)
            self.alg = GrammarAlgorithms(self.grammar)
            
            return {
                "status": "success", 
                "message": "Gramatica guardada con exito.",
                "data": self.grammar.to_dict()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run_algorithm(self, name):
        """Runs the requested algorithm and returns structured data."""
        if not self.grammar or not self.alg:
            return {"status": "error", "message": "Por favor cargue una gramatica primero."}

        try:
            result_data = None
            
            if name == "terminating":
                res, steps = self.alg.compute_terminating_variables()
                result_data = {
                    "type": "set", 
                    "title": "Variables Terminables", 
                    "value": sorted(list(res)),
                    "steps": steps
                }

            elif name == "nullable":
                res, steps = self.alg.compute_nullable_variables()
                result_data = {
                    "type": "set", 
                    "title": "Variables Anulables", 
                    "value": sorted(list(res)),
                    "steps": steps
                }

            elif name == "reachable":
                res, steps = self.alg.compute_reachable_variables()
                result_data = {
                    "type": "set", 
                    "title": "Variables Alcanzables", 
                    "value": sorted(list(res)),
                    "steps": steps
                }

            elif name == "unit":
                res = {}
                steps = []
                for i, v in enumerate(sorted(self.grammar.variables)):
                    closure = self.alg.compute_unit_closure(v)
                    res[v] = sorted(list(closure))
                    steps.append({
                        "iteration": f"Clausura {i+1}",
                        "variables": f"{v} → {{{', '.join(closure)}}}",
                        "explanation": f"Clausura unitaria de {v}",
                        "type": "unit"
                    })
                result_data = {
                    "type": "dict", 
                    "title": "Clausuras unitarias", 
                    "value": res,
                    "steps": steps
                }

            elif name == "useless":
                new_g, steps = self.alg.eliminate_useless_variables()
                result_data = {
                    "type": "grammar", 
                    "title": "Gramatica Simplificada", 
                    "value": new_g.to_dict(),
                    "steps": steps
                }
            
            else:
                return {"status": "error", "message": f"Unknown algorithm: {name}"}

            return {"status": "success", "result": result_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

def start():
    api = AppAPI()
    webview.create_window(
        "CIG Analizador",
        os.path.join(BASE_DIR, "frontend", "index.html"),
        js_api=api,
        width=1200,
        height=850,
        min_size=(900, 600)
    )
    webview.start(debug=False)

if __name__ == "__main__":
    start()