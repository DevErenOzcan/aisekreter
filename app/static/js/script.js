document.addEventListener("DOMContentLoaded", function () {
    const recordToggle = document.getElementById("record-toggle");
    const statusMessage = document.getElementById("status-message");
    const loadingSpinner = document.getElementById("loading-spinner");

    let isRecording = false;
    let meetingId = null; // Used to store the meeting ID

    let ws;
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
                    isRecording = true;
                    record_audio();
                } else {
                    console.error("Meeting başlatılamadı:", response.error);
                }
                $.ajax({
                    url: '/meeting/start_segmentation/' + meetingId + '/',
                    type: 'POST',
                    dataType: 'json',
                    success: function (response) {
                        console.log('Audio sent successfully');
                    },
                    error: function (error) {
                        console.error('Error sending audio:', error);
                    }
                });
            },
            error: function (xhr, status, error) {
                console.error("Hata: ", error);
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
                    // Optionally hide the spinner once processing is done
                } else {
                    console.error("Hata:", response.error);
                }
            },
            error: function (xhr, status, error) {
                console.error("Hata: ", error);
            }
        });
    }

    function record_audio() {
        navigator.mediaDevices.getUserMedia({audio: true})
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start(1000); // 1 saniyelik parçalar halinde kaydet

                mediaRecorder.ondataavailable = event => {
                    if (ws && ws.readyState === WebSocket.OPEN) {
                        ws.send(event.data);
                    }
                };

            })
            .catch(error => console.error("Mikrofona erişim hatası:", error));
    }

    function toggleRecordingState() {
        recordToggle.classList.toggle("recording");
        recordToggle.textContent = isRecording ? "Start Recording" : "Stop Recording";
    }

    function showLoadingSpinner() {
        recordToggle.style.display = "none";
        loadingSpinner.style.display = "block";
    }

    function hideLoadingSpinner() {
        loadingSpinner.style.display = "none";
        recordToggle.style.display = "block";
    }

    function displayTranscriptionResults(data) {
        statusMessage.textContent = "Transcription Complete";

        if (data.speaker_segments) {
            data.speaker_segments.forEach(segment => {
                const segmentCard = document.createElement("div");
                segmentCard.classList.add("segment-card");

                const speakerInfo = document.createElement("h3");
                speakerInfo.classList.add("segment-speaker");
                speakerInfo.textContent = `${segment.speaker}: ${segment.score}`;
                segmentCard.appendChild(speakerInfo);

                const textParagraph = document.createElement("p");
                textParagraph.classList.add("segment-text");
                textParagraph.textContent = segment.text;
                segmentCard.appendChild(textParagraph);

                statusMessage.appendChild(segmentCard);
            });
        }
    }
});
