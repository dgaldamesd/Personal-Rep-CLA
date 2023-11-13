// Archivo JavaScript para resaltar nuevas alertas
function resaltarNuevaAlerta() {
    const tableRows = document.querySelectorAll('.styled-table tbody tr');
    const ultimaFila = tableRows[tableRows.length - 1];
    ultimaFila.classList.add('nueva-alerta');
}

// Llama a la función cuando se cargue la página o después de agregar una nueva alerta
// Ejemplo: después de una solicitud AJAX para agregar una nueva alerta
resaltarNuevaAlerta();
