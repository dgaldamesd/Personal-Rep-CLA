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
