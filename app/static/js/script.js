document.addEventListener("DOMContentLoaded", function () {
    const recordToggle = document.getElementById("record-toggle");
    const statusMessage = document.getElementById("status-message");
    const loadingSpinner = document.getElementById("loading-spinner");

    let isRecording = false;
    let meetingId = null; // Used to store the meeting ID
    let mediaRecorder;

    recordToggle.addEventListener("click", function () {
        isRecording ? stop_meeting() : start_meeting();
        toggleRecordingState();
    });

    function start_meeting() {
        $.ajax({
            url: '/meeting/start/',
            type: 'POST',
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    meetingId = response.id;
                    statusMessage.textContent = "Recording...";
                    navigator.mediaDevices.getUserMedia({audio: true})
                        .then(stream => {
                            mediaRecorder = new MediaRecorder(stream);
                            mediaRecorder.start(5000); // Her 5 saniyede bir veri kaydet
                            isRecording = true;

                            mediaRecorder.ondataavailable = event => {
                                if (event.data.size > 0) {
                                    sendAudio(event.data); // Anında gönder
                                }
                            };
                        })
                        .catch(error => console.error("Mikrofona erişim hatası:", error));
                } else {
                    console.error("Meeting could not be started:", response.error);
                }
            },
            error: function (xhr, status, error) {
                console.error("Error: ", error);
            }
        });
    }

    function stop_meeting() {
        $.ajax({
            url: `/meeting/stop/${meetingId}/`,
            type: 'POST',
            dataType: 'json',
            success: function (response) {
                isRecording = false;
                statusMessage.textContent = "Recording stopped. Processing audio...";
                if (mediaRecorder) {
                    mediaRecorder.stop();
                }
                if (response.success) {
                    showLoadingSpinner();
                } else {
                    console.error("Error:", response.error);
                }
            },
            error: function (xhr, status, error) {
                console.error("Error: ", error);
            }
        });
    }

    function sendAudio(audioBlob) {
        let reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = function () {
            let base64Audio = reader.result.split(',')[1];
            $.ajax({
                url: `/meeting/upload/${meetingId}/`,
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({audio: base64Audio}),
                success: function (response) {
                    console.log("Ses başarıyla yüklendi:", response);
                },
                error: function (xhr, status, error) {
                    console.error("Ses yükleme hatası:", error);
                }
            });
        };
    }


    function toggleRecordingState() {
        recordToggle.classList.toggle("recording");
        recordToggle.textContent = isRecording ? "Stop Recording" : "Start Recording";
    }

    function showLoadingSpinner() {
        recordToggle.style.display = "none";
        loadingSpinner.style.display = "block";
    }

    function hideLoadingSpinner() {
        loadingSpinner.style.display = "none";
        recordToggle.style.display = "block";
    }
});
