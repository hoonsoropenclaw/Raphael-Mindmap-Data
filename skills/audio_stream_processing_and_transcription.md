# Audio Stream Processing and Transcription

## Overview
This micro-skill focuses on processing and transcribing audio streams by leveraging the MediaRecorder API to segment the audio and integrating the Whisper API for transcription. The process involves segmenting the audio stream into manageable chunks, managing the audio queue for processing, and handling transcription through the Whisper API with robust error handling and retry mechanisms.

## Key Components

### 1. Audio Stream Segmentation with MediaRecorder API

#### Explanation
The MediaRecorder API is used to capture and segment the audio stream into discrete, decodable chunks. These chunks are then processed and enqueued for transcription.

#### Key Code Snippets and Patterns
```javascript
function buildSegmentRecorder(mimeType) {
    const recorder = new MediaRecorder(config.mediaStream, mimeType ? { mimeType } : undefined);
    recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) state.pendingChunks.push(event.data);
    };
    recorder.onerror = (event) => {
        log('MediaRecorder 錯誤: ' + (event.error?.message || 'unknown'), 'error');
    };
    return recorder;
}

async function startRecording() {
    const mimeType = pickMimeType();
    state.mediaRecorder = buildSegmentRecorder(mimeType);
    state.mediaRecorder.start();
    setupVisualizer(state.mediaStream);
    state.timerId = setInterval(() => rotateSegment(), parseFloat(els.chunkSec.value) * 1000);
}

function rotateSegment() {
    const recorder = state.mediaRecorder;
    const mimeType = recorder.mimeType || pickMimeType();
    const segmentChunks = [];
    state.pendingChunks = segmentChunks;
    recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) segmentChunks.push(event.data);
    };
    recorder.onstop = () => {
        const blob = new Blob(segmentChunks, { type: mimeType || 'audio/webm' });
        if (blob.size >= 1000) {
            state.audioQueue.push(blob);
            processAudioQueue();
        } else {
            log(`切片太小 (${blob.size}B)，跳過`, 'info');
        }
    };
    recorder.stop();
    if (state.recording && state.mediaStream?.active) {
        state.mediaRecorder = buildSegmentRecorder(mimeType);
        state.mediaRecorder.start();
    }
}
```

#### Common Errors and Prevention
- **Error**: Audio segments are too small to be effectively transcribed.
  **Prevention**: Set a minimum segment size (e.g., 1000 bytes) and skip segments that are too small.
- **Error**: Delays between segments are too long, affecting real-time processing.
  **Prevention**: Adjust the slicing interval to balance latency and audio quality.

### 2. Whisper API Integration for Transcription

#### Explanation
The Whisper API is integrated to transcribe the audio segments. The process includes sending audio blobs to the API, handling responses, and implementing retry mechanisms for transient failures.

#### Key Code Snippets and Patterns
```javascript
async function transcribeBlob(blob) {
    const formData = new FormData();
    formData.append('file', blob, 'audio.webm');
    formData.append('model', 'whisper-1');

    let response;
    for (let attempt = 0; attempt < 3; attempt++) {
        response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
            method: 'POST',
            headers: { 'Authorization': 'Bearer ' + state.apiKey },
            body: formData,
        });
        if (response.ok || ![429, 500, 502, 503, 504].includes(response.status) || attempt === 2) break;
        const delay = 500 * (2 ** attempt);
        log(`API ${response.status}，${delay}ms 後重試`, 'info');
        await new Promise(resolve => setTimeout(resolve, delay));
    }

    if (!response.ok) {
        const errText = await response.text();
        log('API 錯誤: ' + errText, 'error');
        return '';
    }

    const data = await response.json();
    return data.text;
}
```

#### Common Errors and Prevention
- **Error**: API requests fail or return errors.
  **Prevention**: Implement an exponential backoff retry mechanism and handle common error status codes (e.g., 429, 500, 502, 503, 504).
- **Error**: Audio format is not accepted by the API.
  **Prevention**: Ensure that the audio segment's MIME type is correct and validate it before sending.

## Summary
By combining the MediaRecorder API for audio segmentation and the Whisper API for transcription, this micro-skill provides a comprehensive solution for processing and transcribing audio streams. The implementation includes robust error handling and retry mechanisms to ensure reliability and efficiency in various scenarios.