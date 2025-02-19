document.addEventListener("DOMContentLoaded", function () {
    const recordToggle = document.getElementById("record-toggle");
    const statusMessage = document.getElementById("status-message");
    const loadingSpinner = document.getElementById("loading-spinner");

    let isRecording = false;
    let meetingId = null; // Kullanıcı toplantı ID'sini burada saklar.
    let audioContext = null;
    let recorder = null;
    let intervalId;

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
                            audioContext = new (window.AudioContext || window.webkitAudioContext)();
                            const input = audioContext.createMediaStreamSource(stream);
                            recorder = new Recorder(input, {numChannels: 1});

                            const ws = new WebSocket(`ws://127.0.0.1:8080/meeting/${meetingId}/`);

                            ws.onopen = function () {
                                console.log("WebSocket bağlantısı açıldı.");
                                $.ajax({
                                    url: `/meeting/start_segmentation/${meetingId}/`,
                                    type: 'POST',
                                    dataType: 'json',
                                    success: function (response) {
                                        console.log("segmentasyon bitti");
                                    },
                                    error: function (xhr, status, error) {
                                        console.error("Hata:", error);
                                    }
                                });
                                recorder.record(); // Kayıt başlat
                            };

                            ws.onerror = function (error) {
                                console.error("WebSocket hatası:", error);
                            };

                            // Kayıt verilerini gönder
                            intervalId = setInterval(() => {
                                recorder.exportWAV(blob => {
                                    if (!isRecording) {
                                        clearInterval(intervalId); // Kayıt durduğunda interval'i durdur
                                        ws.close()
                                        return; // Kayıt durduysa daha fazla işlem yapma
                                    }
                                    if (ws.readyState === WebSocket.OPEN) {
                                        ws.send(blob);
                                    }
                                    recorder.clear();
                                });
                            }, 5000);
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

                recorder.stop();

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