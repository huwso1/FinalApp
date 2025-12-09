# CIG Analizador - Pyodide Version

Este es el analizador de Gramáticas Libres de Contexto (GLC) convertido para ejecutarse completamente en el navegador usando Pyodide, permitiendo su despliegue en GitHub Pages sin necesidad de un backend.

##  Características

- **100% en el navegador**: Todo el código Python se ejecuta en el navegador usando Pyodide
- **Sin backend necesario**: Ideal para GitHub Pages
- **Misma funcionalidad**: Mantiene todas las características de la versión original
  - Variables Terminables
  - Variables Anulables
  - Variables Alcanzables
  - Clausuras Unitarias
  - Eliminación de Variables Inútiles

##  Estructura de Archivos

```
docs/
├── index.html              # Página principal
├── app.js                  # Lógica de la aplicación y puente con Pyodide
├── styles.css              # Estilos de la interfaz
├── cfg_grammar.py          # Módulo de gramática
├── grammar_algorithms.py   # Algoritmos de análisis
└── README.md              # Esta documentación
```

##  Despliegue en GitHub Pages





## 🧪 Prueba Local

Para probar la aplicación localmente, necesitas un servidor HTTP (los archivos no funcionan directamente con `file://`):

### Usando Python:
```bash
cd docs
python -m http.server 8000
```

### Usando Node.js (npx):
```bash
cd docs
npx http-server -p 8000
```

### Usando PHP:
```bash
cd docs
php -S localhost:8000
```

Luego abre tu navegador en `http://localhost:8000`

##  Uso de la Aplicación

1. **Cargar Gramática**: Ingresa las reglas de producción en el área de texto
   - Formato: `S -> AB | a`
   - Usa `λ` para epsilon (botón de copiar disponible)
   
2. **Ejecutar Análisis**: Haz clic en cualquier botón de análisis
   - Los resultados aparecen en el panel derecho
   - Los pasos detallados se muestran en el panel inferior

3. **Transformar**: Usa "Eliminar variables Inútiles" para simplificar la gramática

##  Diferencias con la Versión Original

- **Carga inicial más lenta**: Pyodide necesita descargar ~10MB la primera vez
- **Sin pywebview**: La interfaz ahora es una página web estándar
- **Sin instalación**: No requiere Python ni dependencias instaladas
- **Funcionamiento idéntico**: Los algoritmos son exactamente los mismos


##  Tecnologías Utilizadas

- **Pyodide 0.24.1**: Ejecución de Python en el navegador
- **Python 3.11**: Lógica de los algoritmos
- **JavaScript ES6+**: Integración y manejo de UI
- **CSS3**: Estilos modernos y responsivos

##  Licencia

Este proyecto mantiene la misma licencia que el original.

##  Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request en el repositorio original.
