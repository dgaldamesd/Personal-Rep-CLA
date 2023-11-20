document.addEventListener("DOMContentLoaded", function() {
    var userElement = document.getElementById("user");
    var langElement = document.getElementById("lang");

    // Verifica si los elementos se están seleccionando correctamente
    console.log(userElement);
    console.log(langElement);

    // Intenta cambiar el texto de los elementos para verificar si se aplican los cambios
    if (userElement) {
        userElement.innerText = "David"; // Cambia el texto del usuario
    } else {
        console.log("Elemento de usuario no encontrado");
    }

    if (langElement) {
        langElement.innerText = "Español"; // Cambia el texto del idioma
    } else {
        console.log("Elemento de idioma no encontrado");
    }
});