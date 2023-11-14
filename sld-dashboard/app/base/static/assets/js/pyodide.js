window.languagePluginUrl = 'https://cdn.jsdelivr.net/pyodide/v0.18.1/full/';
importScripts('https://cdn.jsdelivr.net/pyodide/v0.18.1/full/pyodide.js');

async function main() {
    await loadPyodide();
}
main();

async function runPython() {
    let output = await pyodide.runPythonAsync(`
        import numpy as np
        x = np.array([1, 2, 3, 4, 5])
        y = np.sum(x)
        y
    `);
    document.getElementById("pythonOutput").innerText = "Suma de array: " + output;
}