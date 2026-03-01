        const video = document.getElementById('camera-stream');
        const startButton = document.getElementById('start-camera');

        async function enableCamera() {
            try {
                // Запрашиваем поток с видео
                const stream = await navigator.mediaDevices.getUserMedia({ 
                    video: true, 
                    audio: false 
                });
                
                // Привязываем поток к видеоэлементу
                video.srcObject = stream;
                
                // Делаем кнопку неактивной после успешного запуска
                startButton.disabled = true; 
                startButton.textContent = 'Камера включена';

            } catch (error) {
                console.error('Ошибка доступа к камере:', error);
                alert('Не удалось получить доступ к камере. Пожалуйста, проверьте разрешения и убедитесь, что камера не используется другим приложением.');
            }
        }

        startButton.addEventListener('click', enableCamera);
