
var historyBack = document.getElementById("history-back");
var historyForward = document.getElementById("history-forward");
var speechToTextBtn = document.getElementById("speech-to-text-btn"); // Убедитесь, что id совпадает с тем, что в HTML
var recordAvoiceMessage = document.getElementById("record-a-voice-message");


// Проверяем, существует ли элемент перед установкой обработчика события
if (historyForward) {
    historyForward.onclick = function(event) {
        event.preventDefault();
        window.history.forward();
    }
}
if (historyBack) {
    historyBack.onclick = function(event) {
        event.preventDefault();
        window.history.back();
    }
}
// Проверяем, существует ли элемент перед установкой обработчика события
if (speechToTextBtn) {
    speechToTextBtn.addEventListener("click", function() {
        // Обработка выбора файла
        window.location.href = "/frontend/pages/choice-voice.html";
    });
}

if (recordAvoiceMessage) {
    recordAvoiceMessage.addEventListener("click", function() {
        window.location.href = "/frontend/pages/choice-voice-here.html";
    });
}
