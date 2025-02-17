document.addEventListener("DOMContentLoaded", function () {
    const recordToggle = document.getElementById("record-toggle");
    const statusMessage = document.getElementById("status-message");
    const loadingSpinner = document.getElementById("loading-spinner");

    let isRecording = false;
    let meetingId = null; // Kullanıcı toplantı ID'sini burada saklar.

    // Kayıt butonuna tıklama olayını dinle
    recordToggle.addEventListener("click", function () {
        if (isRecording) {
            stopMeeting();
        } else {
            startMeeting();
        }
        toggleRecordingState();
    });

    // Toplantıyı başlatan fonksiyon
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
                            const audioTrack = stream.getAudioTracks()[0];
                            const peerConnection = new RTCPeerConnection();
                            peerConnection.addTrack(audioTrack, stream);

                            const ws = new WebSocket('ws://127.0.0.1:8080/ws/audio-stream/');

                            ws.onopen = function () {
                                console.log("WebSocket bağlantısı açıldı.");
                                startSendingAudio();
                            };

                            ws.onerror = function (error) {
                                console.error("WebSocket hatası:", error);
                            };

                            function startSendingAudio() {
                                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                                const analyser = audioContext.createAnalyser();
                                const source = audioContext.createMediaStreamSource(stream);
                                source.connect(analyser);

                                const bufferLength = analyser.frequencyBinCount;
                                const dataArray = new Uint8Array(bufferLength);

                                function sendAudioData() {
                                    if (ws.readyState === WebSocket.OPEN) {
                                        analyser.getByteFrequencyData(dataArray);
                                        ws.send(dataArray.buffer); // Send audio data
                                    }

                                    if (isRecording) {
                                        setTimeout(sendAudioData, 1000);
                                    } else {
                                        ws.close();
                                    }
                                }

                                sendAudioData();
                            }
                        })
                        .catch(error => {
                            console.error("Web scoket bağlantısı açılırken hata oluştu", error);
                        });
                } else {
                    console.error("Toplantı başlatılırken bir hata oluştu:", response.error);
                }
            },
            error: function (xhr, status, error) {
                console.error("Hata: ", error);
            }
        });
    }

    // Toplantıyı durduran fonksiyon
    function stopMeeting() {
        $.ajax({
            url: `/meeting/stop/${meetingId}/`,
            type: 'POST',
            dataType: 'json',
            success: function (response) {
                isRecording = false;
                statusMessage.textContent = "Recording stopped. Processing audio...";
                if (response.success) {
                    showLoadingSpinner();
                    console.log("Kayıt durduruldu.");
                } else {
                    console.error("Hata:", response.error);
                }
            },
            error: function (xhr, status, error) {
                console.error("Hata: ", error);
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
