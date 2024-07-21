document.getElementById('record').onclick = function() {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
        mediaRecorder.start();
  
        const audioChunks = [];
        mediaRecorder.addEventListener("dataavailable", event => {
          audioChunks.push(event.data);
        });
  
        mediaRecorder.addEventListener("stop", () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
          const formData = new FormData();
          formData.append('audio', audioBlob);
  
          fetch('/api/transcribe', {
            method: 'POST',
            body: formData
          }).then(response => {
            if (!response.ok) {
              throw new Error('Network response was not ok');
            }
            return response.json();
          }).then(data => {
            document.getElementById('transcript').innerText = data.transcript;
          }).catch(error => {
            console.error('There was a problem with the fetch operation:', error);
          });
        });
  
        setTimeout(() => {
          mediaRecorder.stop();
        }, 5000); // Graba por 5 segundos
      }).catch(error => {
        console.error('There was a problem with getUserMedia:', error);
      });
  };
  
  
  