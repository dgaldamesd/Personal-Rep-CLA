$(document).ready(function(){
    // Función para obtener los valores actuales
    function obtenerValoresActuales() {
        $.ajax({
            url: '/obtener_parametros_actuales',  // Ruta definida en tu Flask para obtener los valores actuales
            type: 'GET',
            success: function(data) {
                // Actualizar los valores en los select
                $('#user').val(data.user);
                $('#lang').val(data.lang);
            },
            error: function(error) {
                console.log('Error al obtener los valores actuales:', error);
            }
        });
    }

    // Llamar a la función al cargar la página para obtener los valores actuales
    obtenerValoresActuales();

    // Intercepta el envío del formulario
    $('form').submit(function(e){
        e.preventDefault();  // Evita la recarga de la página

        // Realiza la solicitud AJAX para actualizar los parámetros
        $.ajax({
            type: 'POST',
            url: '/CONFIG_CALL',
            data: $(this).serialize(),
            success: function(response){
                alert(response); // Muestra una alerta con el mensaje de éxito (puedes cambiar esto según tus necesidades)
                obtenerValoresActuales(); // Vuelve a obtener los valores después de la actualización
            },
            error: function(error) {
                console.log('Error al actualizar los parámetros:', error);
            }
        });
    });
});

window.onload = function() {
    var langElement = document.getElementById('lang');
    var userElement = document.getElementById('user');
    
    if (langElement.innerText.trim() === 'es-ES-Standard-A') {
        langElement.innerText = 'Español';
    }

    if (userElement.innerText.trim() === '+56999641574') {
        userElement.innerText = 'David';
    }

    if (langElement.innerText.trim() === 'en-US-Standard-B') {
        langElement.innerText = 'Inglés';
    }

    if (userElement.innerText.trim() === '+56911111111') {
        userElement.innerText = 'Felipe';
    }
};
