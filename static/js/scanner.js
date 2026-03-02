document.addEventListener('DOMContentLoaded', function() {
    // Получаем элемент видео
    const video = document.getElementById('preview');

    if (!video) {
        alert('Ошибка: элемент video не найден!');
        return;
    }

    // Создаем сканер
    const scanner = new Instascan.Scanner({ video: video });

    // Что делать при сканировании
    scanner.addListener('scan', function(content) {
        console.log('QR код:', content);

        // Показываем результат в простом alert
        alert('Найден QR: ' + content);

        // Отправляем на сервер
        fetch('/scan/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({qr_data: content})
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('Ошибка:', error);
        });
    });

    // Получаем доступ к камерам
    Instascan.Camera.getCameras().then(function(cameras) {
        if (cameras.length > 0) {
            scanner.start(cameras[0]); // Запускаем первую камеру
            console.log('Камера запущена');
        } else {
            alert('Камера не найдена');
        }
    }).catch(function(error) {
        alert('Ошибка доступа к камере: ' + error);
    });

    // Функция для получения CSRF-токена
    function getCookie(name) {
        let value = '; ' + document.cookie;
        let parts = value.split('; ' + name + '=');
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
    }
});