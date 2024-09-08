document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');
    const resumeBtn = document.getElementById('resume-btn');
    const completeBtn = document.getElementById('complete-btn');
    const controls = document.getElementById('controls');
    const waves = document.querySelectorAll('.wave');
    const dialog = document.getElementById('dialog');
    const closeBtn = document.getElementById('close-btn');
    const dialogText = document.getElementById('dialog-text');

    let isRecording = false;
    let mediaRecorder;
    let audioChunks = [];
    let audioBlob;
    let isPaused = false;

    // Поддерживаемые форматы
    const supportedMimeTypes = ['audio/webm', 'audio/ogg', 'audio/mp4'];
    const mimeType = supportedMimeTypes.find(type => MediaRecorder.isTypeSupported(type)) || 'audio/webm';

    // Начало записи
    async function startRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType });

            mediaRecorder.ondataavailable = event => {
                console.log('ondataavailable: ', event.data);
                if (event.data.size > 0) {
                    audioChunks.push(event.data);
                } else {
                    console.log('Получены пустые данные');
                }
            };

            mediaRecorder.onstop = () => {
                console.log('onstop: ', audioChunks);
                if (audioChunks.length > 0) {
                    audioBlob = new Blob(audioChunks, { type: mimeType });
                    audioChunks = [];
                    console.log('Запись завершена, создан Blob', audioBlob);
                    sendAudioToServer();
                    saveAudioLocally();
                } else {
                    console.log('Нет данных для создания Blob');
                }
            };

            mediaRecorder.start();
            isRecording = true;
            startWaves();
            console.log('Запись начата с MIME типом:', mimeType);
        } catch (err) {
            console.error('Ошибка доступа к микрофону:', err);
        }
    }

    function pauseRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.pause();
            isPaused = true;
            stopWaves();
            console.log('Запись приостановлена');
        }
    }

    function resumeRecording() {
        if (mediaRecorder && isPaused) {
            mediaRecorder.resume();
            isPaused = false;
            startWaves();
            console.log('Запись возобновлена');
        }
    }

    function stopRecording() {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            isRecording = false;
            console.log('Запись остановлена');
        }
    }

    function sendAudioToServer() {
        if (audioBlob) {
            console.log('Отправка аудиофайла на сервер...');

            const formData = new FormData();
            formData.append('file', audioBlob, `recording.${mimeType.split('/')[1]}`);

            fetch('/audio-transcription/upload?token=1234&model=medium&language=ru', {
                method: 'POST',
                body: formData,
                headers: {
                    'Accept': 'application/json'
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Ошибка сети: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Успешно отправлено:', data);
            })
            .catch(error => {
                console.error('Ошибка при отправке аудио:', error);
            });
        } else {
            console.log('Нет данных для отправки');
        }
    }

    function saveAudioLocally() {
        if (audioBlob) {
            const url = URL.createObjectURL(audioBlob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `recording.${mimeType.split('/')[1]}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            console.log(`Файл сохранён локально как recording.${mimeType.split('/')[1]}`);
        } else {
            console.log('Нет данных для сохранения');
        }
    }

    startBtn.addEventListener('click', () => {
        startBtn.classList.add('hidden');
        controls.classList.remove('hidden');
        startRecording();
    });

    stopBtn.addEventListener('click', () => {
        stopBtn.classList.add('hidden');
        resumeBtn.classList.remove('hidden');
        pauseRecording();
    });

    resumeBtn.addEventListener('click', () => {
        stopBtn.classList.remove('hidden');
        resumeBtn.classList.add('hidden');
        resumeRecording();
    });

    completeBtn.addEventListener('click', () => {
        dialog.classList.remove('hidden');
        stopRecording();
        dialogText.textContent = "Запись завершена.";
    });

    closeBtn.addEventListener('click', () => {
        closeDialog();
    });

    function closeDialog() {
        dialog.classList.add('hidden');
        controls.classList.add('hidden');
        startBtn.classList.remove('hidden');
    }

    function startWaves() {
        waves.forEach(wave => {
            wave.style.opacity = 1;
            wave.style.animationPlayState = 'running';
        });
    }

    function stopWaves() {
        waves.forEach(wave => {
            wave.style.opacity = 0;
            wave.style.animationPlayState = 'paused';
        });
    }
});
