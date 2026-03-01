// Инициализация сканера QR-кодов
document.addEventListener('DOMContentLoaded', function() {
    let scanner = new Instascan.Scanner({
        video: document.getElementById('preview'),
        scanPeriod: 5,
        mirror: false
    });

    scanner.addListener('scan', function(content) {
        // При успешном сканировании отправляем данные на сервер
        scanQRCode(content);
    });

    // Запрос доступа к камере и запуск сканера
    Instascan.Camera.getCameras().then(function(cameras) {
        if (cameras.length > 0) {
            // Используем заднюю камеру если доступна
            let backCamera = cameras.find(camera => camera.name.toLowerCase().includes('back'));
            scanner.start(backCamera || cameras[0]);

            // Показываем индикатор готовности
            showNotification('Камера готова к работе', 'success');
        } else {
            showNotification('Камера не найдена', 'error');
        }
    }).catch(function(error) {
        console.error('Ошибка доступа к камере:', error);
        showNotification('Ошибка доступа к камере', 'error');
    });

    // Функция отправки QR-кода на сервер
    function scanQRCode(qrData) {
        fetch('/scan/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({qr_data: qrData})
        })
        .then(response => response.json())
        .then(data => {
            displayResult(data);
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showNotification('Ошибка связи с сервером', 'error');
        });
    }

    // Отображение результата проверки
    function displayResult(data) {
        const resultDiv = document.getElementById('result');
        const resultContent = document.getElementById('result-content');

        // Убираем скрытие
        resultDiv.classList.remove('hidden');

        // Устанавливаем класс в зависимости от результата
        resultDiv.className = 'result-card';
        resultDiv.classList.add(data.result);

        // Формируем содержимое
        let html = `<div class="result-content">`;

        if (data.pass_data && data.pass_data.photo) {
            html += `<img src="${data.pass_data.photo}" class="pass-photo">`;
        }

        html += `<div class="pass-info">
            <h4>${data.message}</h4>`;

        if (data.pass_data) {
            html += `
                <p><strong>${data.pass_data.full_name}</strong></p>
                <p>${data.pass_data.pass_type}</p>
                <p>${data.pass_data.organization || ''}</p>
            `;
        }

        html += `</div></div>`;

        resultContent.innerHTML = html;

        // Звуковой сигнал
        playSound(data.result);
    }

    // Звуковое оповещение
    function playSound(result) {
        let audio = new Audio();
        if (result === 'granted') {
            audio.src = 'data:audio/wav;base64,//uQ...'; // Здесь base64 звука успеха
        } else {
            audio.src = 'data:audio/wav;base64,//uQ...'; // Здесь base64 звука отказа
        }
        audio.play().catch(e => console.log('Аудио не поддерживается'));
    }

    // Уведомления
    function showNotification(message, type) {
        // Создаем элемент уведомления
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        // Удаляем через 3 секунды
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Функция для получения CSRF-токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            let cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                let cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});