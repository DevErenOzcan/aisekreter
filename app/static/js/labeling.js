document.addEventListener("DOMContentLoaded", function () {
    const recordToggle = document.getElementById("record-toggle");
    const audioPlayback = document.getElementById("audio-playback");
    const audioContainer = document.getElementById("audio-container");
    const speakerNameInput = document.getElementById("speaker_name");
    const statusMessage = document.getElementById("status-message");

    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    // Disable the button if speaker name is empty
    speakerNameInput.addEventListener("input", function () {
        if (speakerNameInput.value.trim() === "") {
            recordToggle.disabled = true;
            recordToggle.classList.add("disabled");
        } else {
            recordToggle.disabled = false;
            recordToggle.classList.remove("disabled");
        }
    });

    // Initially disable the button
    recordToggle.disabled = true;

    // Toggle recording
    recordToggle.addEventListener("click", function () {
        isRecording ? stopRecording() : startRecording();
        toggleRecordingState();
    });

    // Start recording function
    function startRecording() {
        const speakerName = speakerNameInput.value.trim();
        if (!speakerName) {
            statusMessage.textContent = "Please enter a speaker name before recording.";
            return;
        }

        audioChunks = [];
        statusMessage.textContent = "Recording...";

        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                isRecording = true;

                mediaRecorder.ondataavailable = event => {
                    audioChunks.push(event.data);
                };
            })
            .catch(error => {
                console.error("Error accessing microphone:", error);
                statusMessage.textContent = "Error accessing microphone. Please check your permissions.";
            });
    }

    // Stop recording function
    function stopRecording() {
        if (!mediaRecorder) {
            console.warn("MediaRecorder is not initialized.");
            return;
        }

        mediaRecorder.stop();
        isRecording = false;
        statusMessage.textContent = "Recording stopped. Processing audio...";

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const audioUrl = URL.createObjectURL(audioBlob);
            audioPlayback.src = audioUrl;

            // Show the audio container
            audioContainer.classList.remove("hidden");

            // Upload the audio
            uploadAudio(audioBlob);
        };
    }

    // Toggle recording state
    function toggleRecordingState() {
        recordToggle.classList.toggle("recording");
        recordToggle.textContent = isRecording ? "Start Recording" : "Stop Recording";
    }

    // Function to upload audio to the server
    function uploadAudio(audioBlob) {
        const speakerName = speakerNameInput.value.trim();
        const formData = new FormData();
        formData.append("audio_file", audioBlob, `${speakerName}.wav`);
        formData.append("speaker_name", speakerName);

        fetch("/person_labeling/", {
            method: "POST",
            body: formData,
        })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error("Failed to upload audio.");
                }
            })
            .then(data => {
                statusMessage.textContent = "Audio uploaded successfully!";
                console.log("Server response:", data);
                recordToggle.textContent = "Transcribe New Audio";

            })
            .catch(error => {
                console.error("Error uploading audio:", error);
                statusMessage.textContent = "Failed to upload audio. Please try again.";
                recordToggle.textContent = "Transcribe New Audio";
            });
    }
});
