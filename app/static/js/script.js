document.addEventListener("DOMContentLoaded", function () {
    const recordToggle = document.getElementById("record-toggle");
    const statusMessage = document.getElementById("status-message");

    let isRecording = false;
    let audioContext = null;
    let recorder = null;
    let intervalId;

    recordToggle.addEventListener("click", function () {
        if (isRecording) {
            stopMeeting();
        } else {
            startMeeting();
        }
        toggleRecordingState();
    });

    function startMeeting() {
        isRecording = true;
        statusMessage.textContent = "Recording...";
        navigator.mediaDevices.getUserMedia({audio: true})
            .then(stream => {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const input = audioContext.createMediaStreamSource(stream);
                recorder = new Recorder(input, {numChannels: 1});

                const ws = new WebSocket(`ws://127.0.0.1:8080/meeting/`);

                ws.onopen = function () {
                    console.log("WebSocket bağlantısı açıldı.");
                    recorder.record();
                };
                ws.onerror = function (error) {
                    console.error("WebSocket hatası:", error);
                };
                ws.onmessage = function (event) {
                    const data = JSON.parse(event.data);
                    console.log(data);
                    displayResult(data);
                };

                intervalId = setInterval(() => {
                    recorder.exportWAV(blob => {
                        if (!isRecording) {
                            clearInterval(intervalId);
                            ws.close();
                            return;
                        }
                        if (ws.readyState === WebSocket.OPEN) {
                            ws.send(blob);
                        }
                        recorder.clear();
                    });
                }, 1000);
            })
            .catch(error => {
                console.error("Mikrofon erişim hatası:", error);
            });
    }

    function stopMeeting() {
        isRecording = false;
        statusMessage.textContent = "Recording stopped";
        recorder.stop();
    }

    function toggleRecordingState() {
        recordToggle.classList.toggle("recording");
        recordToggle.textContent = isRecording ? "Stop Recording" : "Start Recording";
    }

    function displayResult(data) {
        let outputDiv = document.getElementById("output");
        let table = outputDiv.querySelector("table");

        // Eğer tablo yoksa, oluştur ve başlık satırını ekle
        if (!table) {
            table = document.createElement("table");
            table.style.width = "100%";
            table.style.borderCollapse = "collapse";

            // Tablo başlığını oluştur
            let thead = document.createElement("thead");
            let headerRow = document.createElement("tr");

            ["ID", "Text", "Sentiment"].forEach(text => {
                let th = document.createElement("th");
                th.textContent = text;
                th.style.border = "1px solid black";
                th.style.padding = "8px";
                th.style.textAlign = "left";
                headerRow.appendChild(th);
            });

            thead.appendChild(headerRow);
            table.appendChild(thead);

            // Tablo gövdesini oluştur
            let tbody = document.createElement("tbody");
            table.appendChild(tbody);

            outputDiv.appendChild(table);
        }

        // Yeni satırı oluştur
        let tbody = table.querySelector("tbody");
        let row = document.createElement("tr");

        [data.id, data.text, data.audio_sentiment].forEach(text => {
            let td = document.createElement("td");
            td.textContent = text;
            td.style.border = "1px solid black";
            td.style.padding = "8px";
            row.appendChild(td);
        });

        tbody.appendChild(row);
    }

});
