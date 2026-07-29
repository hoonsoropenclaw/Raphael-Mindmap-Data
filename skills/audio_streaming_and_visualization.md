# Audio Streaming and Visualization

## Overview
This micro-skill focuses on implementing real-time audio streaming, processing, and visualization using the Whisper API, MediaRecorder API, and Canvas API. The goal is to create a cohesive system that captures audio, transcribes it in near real-time, and visualizes the audio stream for enhanced user experience in applications such as voice assistants, transcription services, and audio analysis tools.

## Key Components

### 1. Whisper API Streaming Adapter
**Purpose**: Convert the Whisper API's batch processing mode into a near real-time speech-to-text application by slicing the audio stream into smaller segments and uploading them continuously.

#### Key Code Snippets and Patterns
- **Audio Slicing**: Use the `MediaRecorder` API to slice the audio stream at fixed intervals (e.g., every 2 seconds).
  ```javascript
  const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      // Upload the audio chunk
      uploadAudioChunk(event.data);
    }
  };
  mediaRecorder.start(2000); // Slice every 2 seconds
  ```
- **API Call Integration**: Upload each audio chunk to the Whisper API and handle the returned transcription.
  ```javascript
  async function uploadAudioChunk(blob) {
    const formData = new FormData();
    formData.append('file', blob, 'audio.webm');
    formData.append('model', 'whisper-1');
    try {
      const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer YOUR_API_KEY`,
        },
        body: formData,
      });
      const data = await response.json();
      // Process the transcription result
      updateTranscript(data.text);
    } catch (error) {
      console.error('Error uploading audio chunk:', error);
      // Implement retry logic or error handling
    }
  }
  ```
- **Result Concatenation**: Concatenate each transcription result in sequence to display continuous text.
  ```javascript
  let transcript = '';
  function updateTranscript(newText) {
    transcript += ' ' + newText;
    document.getElementById('transcript').innerText = transcript.trim();
  }
  ```

#### Common Errors and Prevention
- **Improper Chunk Size**: Small chunks may lead to excessive API calls, while large chunks increase latency. Adjust chunk size based on the application scenario, e.g., 2 seconds per chunk.
- **API Call Failures**: Network instability or API rate limits may cause call failures. Implement retry mechanisms and error handling logic.
- **Resource Management**: For long-running applications, ensure proper memory and resource management to prevent leaks and high resource usage.

### 2. MediaRecorder Audio Processing
**Purpose**: Utilize the MediaRecorder API to capture audio streams and process them, such as slicing, noise reduction, and encoding.

#### Key Code Snippets and Patterns
- **Initialize MediaRecorder**:
  ```javascript
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
  ```
- **Handle Data Available Event**:
  ```javascript
  mediaRecorder.ondataavailable = (event) => {
    if (event.data.size > 0) {
      // Process the audio chunk, e.g., upload or local processing
      processAudioChunk(event.data);
    }
  };
  ```
- **Start and Stop Recording**:
  ```javascript
  mediaRecorder.start(2000); // Slice every 2 seconds
  // Stop recording
  mediaRecorder.stop();
  ```

#### Common Errors and Prevention
- **Permission Issues**: Users may deny microphone access, leading to recording failure. Prompt users for permission and handle denial scenarios.
- **Browser Compatibility**: Different browsers have varying support for the MediaRecorder API. Perform compatibility testing across target browsers.
- **Resource Release**: After recording, ensure the MediaRecorder is stopped and audio stream resources are released to prevent resource leaks.

### 3. Audio Stream Visualization
**Purpose**: Use the Canvas API to visualize audio stream data, such as displaying waveforms or frequency spectra.

#### Key Code Snippets and Patterns
- **Retrieve Audio Data**:
  ```javascript
  const audioContext = new AudioContext();
  const analyser = audioContext.createAnalyser();
  const source = audioContext.createMediaStreamSource(stream);
  source.connect(analyser);
  ```
- **Draw Waveform**:
  ```javascript
  function draw() {
    requestAnimationFrame(draw);
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);
    // Use Canvas API to draw the data
    const canvas = document.getElementById('visualization');
    const canvasContext = canvas.getContext('2d');
    canvasContext.clearRect(0, 0, canvas.width, canvas.height);
    // Example: Draw a simple bar chart
    const barWidth = canvas.width / analyser.frequencyBinCount;
    for (let i = 0; i < analyser.frequencyBinCount; i++) {
      const barHeight = dataArray[i];
      const x = i * barWidth;
      const y = canvas.height - barHeight;
      canvasContext.fillStyle = 'rgb(0, 0, 0)';
      canvasContext.fillRect(x, y, barWidth, barHeight);
    }
  }
  draw();
  ```

#### Common Errors and Prevention
- **Performance Issues**: Frequent drawing operations can cause performance bottlenecks. Optimize drawing logic by reducing the drawing frequency or simplifying the content.
- **Audio Data Retrieval Failures**: Ensure the audio stream is correctly connected to the analyser and handle interruptions in the audio stream.

## Best Practices
- **Error Handling**: Implement comprehensive error handling for all API calls and asynchronous operations to ensure the application remains robust under unexpected conditions.
- **User Experience**: Provide clear feedback to users during audio processing and visualization, such as loading indicators or visual cues when the audio stream is active.
- **Performance Optimization**: Continuously monitor and optimize the application's performance, especially for resource-intensive tasks like real-time audio processing and visualization.

## Conclusion
By integrating the Whisper API, MediaRecorder API, and Canvas API, this micro-skill enables the development of sophisticated real-time audio applications that not only transcribe audio but also provide insightful visualizations. Adhering to best practices and being mindful of common pitfalls will ensure the application is both efficient and user-friendly.