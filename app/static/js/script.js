document.addEventListener("DOMContentLoaded", function () {
    const recordToggle = document.getElementById("record-toggle");
    const statusMessage = document.getElementById("status-message");
    const loadingSpinner = document.getElementById("loading-spinner");

    let isRecording = false;
    let meetingId = null; // Kullanıcı toplantı ID'sini burada saklar.
    let mediaRecorder = null

    // Kayıt butonuna tıklama olayını dinle
    recordToggle.addEventListener("click", function () {
        if (isRecording) {
            stopMeeting();
        } else {
            startMeeting();
        }
        toggleRecordingState();
    });

    function startMeeting() {
        $.ajax({
            url: '/meeting/start/',
            type: 'POST',
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    meetingId = response.id;
                    isRecording = true;
                    statusMessage.textContent = "Recording...";

                    navigator.mediaDevices.getUserMedia({audio: true})
                        .then(stream => {
                            mediaRecorder = new MediaRecorder(stream, {mimeType: 'audio/webm'});
                            const ws = new WebSocket(`ws://127.0.0.1:8080/meeting/${meetingId}/`);

                            ws.onopen = function () {
                                console.log("WebSocket bağlantısı açıldı.");
                                mediaRecorder.start(1000); // Her 1 saniyede bir veri gönder
                            };

                            ws.onerror = function (error) {
                                console.error("WebSocket hatası:", error);
                            };

                            mediaRecorder.ondataavailable = function (event) {
                                if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
                                    ws.send(event.data);
                                }
                            };

                            mediaRecorder.onstop = function () {
                                console.log("Kayıt durduruldu.");
                                ws.close();
                            };
                        })
                        .catch(error => {
                            console.error("Mikrofon erişim hatası:", error);
                        });
                } else {
                    console.error("Toplantı başlatılırken hata oluştu:", response.error);
                }
            },
            error: function (xhr, status, error) {
                console.error("Hata:", error);
            }
        });
    }

    function stopMeeting() {
        $.ajax({
            url: `/meeting/stop/${meetingId}/`,
            type: 'POST',
            dataType: 'json',
            success: function (response) {
                isRecording = false;
                statusMessage.textContent = "Recording stopped. Processing audio...";

                if (mediaRecorder && mediaRecorder.state !== "inactive") {
                    mediaRecorder.stop();
                }

                if (response.success) {
                    showLoadingSpinner();
                } else {
                    console.error("Hata:", response.error);
                }
            },
            error: function (xhr, status, error) {
                console.error("Hata:", error);
            }
        });
    }

    // Kayıt durumunu göster ve buton metnini güncelle
    function toggleRecordingState() {
        recordToggle.classList.toggle("recording");
        recordToggle.textContent = isRecording ? "Stop Recording" : "Start Recording";
    }

    // Yükleme simgesini göster
    function showLoadingSpinner() {
        recordToggle.style.display = "none";
        loadingSpinner.style.display = "block";
    }

    // Yükleme simgesini gizle
    function hideLoadingSpinner() {
        loadingSpinner.style.display = "none";
        recordToggle.style.display = "block";
    }
});
