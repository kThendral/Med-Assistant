let mediaRecorder;
let audioChunks = [];

document.getElementById("recordBtn").onclick = async () => {
  if (!mediaRecorder || mediaRecorder.state === "inactive") {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
      const blob = new Blob(audioChunks, { type: "audio/wav" });
      const formData = new FormData();
      formData.append("audio", blob, "recording.wav");

      const response = await fetch("/upload", {
        method: "POST",
        body: formData,
      });

      const result = await response.text();
      document.getElementById("result").innerText = result;
    };

    setTimeout(() => mediaRecorder.stop(), 5000); // auto stop after 5 seconds
  }
};
