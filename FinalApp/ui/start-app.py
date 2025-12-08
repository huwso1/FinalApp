import webview
import os
import sys
import json

# Correct path resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Core is one level up from ui/
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
                raise ValueError("Input is empty.")

            self.grammar = CFGGrammar(productions=lines)
            self.alg = GrammarAlgorithms(self.grammar)
            
            return {
                "status": "success", 
                "message": "Grammar loaded successfully.",
                "data": self.grammar.to_dict()
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run_algorithm(self, name):
        """Runs the requested algorithm and returns structured data."""
        if not self.grammar or not self.alg:
            return {"status": "error", "message": "Please load a grammar first."}

        try:
            result_data = None
            
            if name == "terminating":
                res = self.alg.compute_terminating_variables()
                result_data = {"type": "set", "title": "Terminating Variables", "value": sorted(list(res))}

            elif name == "nullable":
                res = self.alg.compute_nullable_variables()
                result_data = {"type": "set", "title": "Nullable Variables", "value": sorted(list(res))}

            elif name == "reachable":
                res = self.alg.compute_reachable_variables()
                result_data = {"type": "set", "title": "Reachable Variables", "value": sorted(list(res))}

            elif name == "unit":
                res = {}
                for v in sorted(self.grammar.variables):
                    res[v] = sorted(list(self.alg.compute_unit_closure(v)))
                result_data = {"type": "dict", "title": "Unit Closures", "value": res}

            elif name == "useless":
                new_g = self.alg.eliminate_useless_variables()
                result_data = {"type": "grammar", "title": "Simplified Grammar", "value": new_g.to_dict()}
            
            else:
                return {"status": "error", "message": f"Unknown algorithm: {name}"}

            return {"status": "success", "result": result_data}

        except Exception as e:
            return {"status": "error", "message": str(e)}

def start():
    api = AppAPI()
    webview.create_window(
        "CFG Analyzer Pro",
        os.path.join(BASE_DIR, "frontend", "index.html"),
        js_api=api,
        width=1200,
        height=850,
        min_size=(900, 600)
    )
    webview.start(debug=True) # Debug enabled for F12 dev tools

if __name__ == "__main__":
    start()