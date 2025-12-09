// Global variables
let pyodide = null;
let appAPI = null;

// Initialize Pyodide and load Python modules
async function initializePyodide() {
    const loadingIndicator = document.getElementById('loading-indicator');
    const appControls = document.getElementById('app-controls');
    
    try {
        loadingIndicator.querySelector('p').textContent = 'Cargando Pyodide...';
        
        // Load Pyodide
        pyodide = await loadPyodide();
        
        loadingIndicator.querySelector('p').textContent = 'Cargando módulos Python...';
        
        // Load Python files
        const cfgGrammarResponse = await fetch('cfg_grammar.py');
        const cfgGrammarCode = await cfgGrammarResponse.text();
        
        const grammarAlgorithmsResponse = await fetch('grammar_algorithms.py');
        const grammarAlgorithmsCode = await grammarAlgorithmsResponse.text();
        
        // Load modules into Pyodide
        await pyodide.runPythonAsync(cfgGrammarCode);
        await pyodide.runPythonAsync(grammarAlgorithmsCode);
        
        // Create AppAPI class in Python
        await pyodide.runPythonAsync(`
class AppAPI:
    def __init__(self):
        self.grammar = None
        self.alg = None

    def load_grammar(self, productions_text):
        """Parses grammar from frontend input."""
        try:
            lines = [ln.strip() for ln in productions_text.split("\\n") if ln.strip()]
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

# Create global API instance
api = AppAPI()
        `);
        
        // Get reference to Python API
        appAPI = pyodide.globals.get('api');
        
        // Hide loading, show controls
        loadingIndicator.style.display = 'none';
        appControls.style.display = 'block';
        
        showToast('Aplicación lista para usar', false);
        
    } catch (error) {
        console.error('Error initializing Pyodide:', error);
        loadingIndicator.innerHTML = `
            <div style="color: #ef4444;">
                <p>Error al cargar la aplicación</p>
                <p style="font-size: 0.8rem;">${error.message}</p>
            </div>
        `;
    }
}

// UI Helper Functions
function showToast(msg, isError = false) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.className = isError ? "error show" : "show";
    setTimeout(() => toast.className = toast.className.replace("show", ""), 3000);
}

function renderResult(data) {
    const outputContainer = document.getElementById('output-container');
    outputContainer.innerHTML = "";

    const title = document.createElement("h3");
    title.style.margin = "0 0 15px 0";
    title.style.color = "#334155";
    title.textContent = data.title;
    outputContainer.appendChild(title);

    if (data.type === "set") {
        if (data.value.length === 0) {
            outputContainer.innerHTML += "<em>Conjunto vacío</em>";
        } else {
            data.value.forEach(item => {
                const badge = document.createElement("span");
                badge.className = "badge";
                badge.textContent = item;
                outputContainer.appendChild(badge);
            });
        }
    } 
    else if (data.type === "dict") {
        for (const [key, val] of Object.entries(data.value)) {
            const row = document.createElement("div");
            row.className = "table-row";
            row.innerHTML = `<span class="table-key">${key}</span> <span class="arrow">→</span> <span>{ ${val.join(", ")} }</span>`;
            outputContainer.appendChild(row);
        }
    } 
    else if (data.type === "grammar") {
        renderGrammar(data.value, null, true);
    }
    
    // Show steps
    if (data.steps) {
        renderSteps(data.steps, data.title);
    } else {
        clearSteps();
    }
}

function renderGrammar(grammarData, customTitle, append = false) {
    const outputContainer = document.getElementById('output-container');
    if (!append) outputContainer.innerHTML = "";
    
    if (customTitle) {
        const h3 = document.createElement("h3");
        h3.textContent = customTitle;
        outputContainer.appendChild(h3);
    }

    const stats = document.createElement("div");
    stats.style.marginBottom = "15px";
    stats.style.fontSize = "0.9rem";
    stats.innerHTML = `
        <strong>Símbolo Inicial:</strong> <span class="badge">${grammarData.start}</span>
        <strong>Variables:</strong> ${grammarData.variables.length}
        <strong>Terminales:</strong> ${grammarData.terminals.length}
    `;
    outputContainer.appendChild(stats);

    const prodContainer = document.createElement("div");
    prodContainer.style.background = "#f8fafc";
    prodContainer.style.padding = "10px";
    prodContainer.style.borderRadius = "6px";

    for (const [lhs, rhsList] of Object.entries(grammarData.productions)) {
        const row = document.createElement("div");
        row.className = "table-row";
        const displayRhs = rhsList.map(r => r === "λ" ? "λ" : r).join(" | ");
        row.innerHTML = `<span class="table-key">${lhs}</span> <span class="arrow">→</span> <span class="prod-list">${displayRhs}</span>`;
        prodContainer.appendChild(row);
    }
    outputContainer.appendChild(prodContainer);
}

function renderSteps(steps, title) {
    const stepsContent = document.getElementById('steps-content');
    stepsContent.innerHTML = "";
    
    if (!steps || steps.length === 0) {
        stepsContent.innerHTML = '<p style="color: #94a3b8; font-style: italic;">No hay pasos para mostrar.</p>';
        return;
    }
    
    // Algorithm title
    const h4 = document.createElement("h4");
    h4.style.margin = "0 0 15px 0";
    h4.style.color = "#334155";
    h4.textContent = title || "Proceso del Algoritmo";
    stepsContent.appendChild(h4);
    
    // Show each step
    steps.forEach((step, index) => {
        const stepDiv = document.createElement("div");
        stepDiv.className = `step-item ${step.type || ""}`;
        
        const header = document.createElement("div");
        header.className = "step-header";
        
        const iteration = document.createElement("span");
        iteration.className = "step-iteration";
        iteration.textContent = step.iteration || `Paso ${index + 1}`;
        
        const vars = document.createElement("span");
        vars.className = "step-vars";
        vars.textContent = step.variables || step.result || "";
        
        header.appendChild(iteration);
        header.appendChild(vars);
        stepDiv.appendChild(header);
        
        if (step.explanation) {
            const explanation = document.createElement("div");
            explanation.className = "step-rule";
            explanation.textContent = step.explanation;
            stepDiv.appendChild(explanation);
        }
        
        if (step.newVariables && step.newVariables.length > 0) {
            const newVars = document.createElement("div");
            newVars.className = "step-rule";
            newVars.innerHTML = `<strong style="color: #059669;">Añadidas:</strong> ${step.newVariables.join(", ")}`;
            newVars.style.marginTop = "4px";
            stepDiv.appendChild(newVars);
        }
        
        stepsContent.appendChild(stepDiv);
    });
}

function clearSteps() {
    const stepsContent = document.getElementById('steps-content');
    stepsContent.innerHTML = '<p style="color: #94a3b8; font-style: italic; margin: 0;">Seleccione un algoritmo para ver los pasos detallados...</p>';
}

// Event Handlers
async function handleLoadGrammar() {
    const grammarInput = document.getElementById("grammar-input");
    const text = grammarInput.value;
    
    try {
        const result = appAPI.load_grammar(text);
        const res = result.toJs({dict_converter: Object.fromEntries});
        
        if (res.status === "error") {
            showToast(res.message, true);
        } else {
            showToast("Gramática cargada correctamente.");
            renderGrammar(res.data, "Estructura Actual de la Gramática");
            clearSteps();
        }
    } catch (error) {
        showToast("Error: " + error.message, true);
    }
}

async function handleRunAlgorithm(op) {
    try {
        const result = appAPI.run_algorithm(op);
        const res = result.toJs({dict_converter: Object.fromEntries});

        if (res.status === "error") {
            showToast(res.message, true);
        } else {
            renderResult(res.result);
        }
    } catch (error) {
        showToast("Error: " + error.message, true);
    }
}

// Initialize when page loads
window.addEventListener('DOMContentLoaded', () => {
    // Initialize Pyodide
    initializePyodide();
    
    // Load grammar button
    document.getElementById("load-btn").addEventListener('click', handleLoadGrammar);
    
    // Algorithm buttons
    document.querySelectorAll(".op-btn").forEach(btn => {
        btn.addEventListener('click', function() {
            // Remove active class from all buttons
            document.querySelectorAll(".op-btn").forEach(b => b.classList.remove("active"));
            // Add active class to clicked button
            this.classList.add("active");
            
            const op = this.getAttribute("data-op");
            handleRunAlgorithm(op);
        });
    });
    
    // Lambda copy button
    document.getElementById('copy-lambda-btn').addEventListener('click', () => {
        navigator.clipboard.writeText('λ').then(() => {
            const msg = document.getElementById('copy-msg');
            msg.style.display = 'block';
            setTimeout(() => { msg.style.display = 'none'; }, 2000);
        }).catch(err => {
            console.error('Error al copiar:', err);
        });
    });
});
