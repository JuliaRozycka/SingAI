// Access the camera and display the video stream
function startCamera() {
    const video = document.getElementById('video');

    navigator.mediaDevices.getUserMedia({video: true})
        .then((stream) => {
            video.srcObject = stream;
            video.play(); // Ensure video starts playing
            captureFrame(); // Start capturing frames
        })
        .catch((error) => {
            console.error("Error accessing the camera: ", error);
        });
}

// Handle camera toggle
document.getElementById('cameraToggle').addEventListener('change', function () {
    const video = document.getElementById('video');
    const subtitlesToggle = document.getElementById('subtitlesToggle');
    const cameraIcon = document.querySelector('.fa-camera');
    const subtitlesIcon = document.querySelector('.fa-closed-captioning');

    if (this.checked) {
        startCamera();
        video.classList.remove('gray-screen');
        subtitlesToggle.disabled = false;
        cameraIcon.classList.remove('inactive');
        subtitlesIcon.classList.add('inactive');
    } else {
        const stream = video.srcObject;
        if (stream) {
            const tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
        }
        video.srcObject = null;
        video.classList.add('gray-screen');
        subtitlesToggle.disabled = true;
        subtitlesToggle.checked = false;
        document.getElementById('output').classList.add('hidden-text');
        cameraIcon.classList.add('inactive');
        subtitlesIcon.classList.add('inactive');
    }
});

// Handle subtitles toggle
document.getElementById('subtitlesToggle').addEventListener('change', function () {
    const output = document.getElementById('output');
    const subtitlesIcon = document.querySelector('.fa-closed-captioning');

    if (this.checked) {
        output.classList.remove('hidden-text');
        subtitlesIcon.classList.remove('inactive');
    } else {
        output.classList.add('hidden-text');
        subtitlesIcon.classList.add('inactive');
    }
});

// Initialize toggles in the off state when the page loads
window.addEventListener('load', function () {
    const cameraToggle = document.getElementById('cameraToggle');
    const subtitlesToggle = document.getElementById('subtitlesToggle');
    const cameraIcon = document.querySelector('.fa-camera');
    const subtitlesIcon = document.querySelector('.fa-closed-captioning');
    const video = document.getElementById('video');

    cameraToggle.checked = false;
    subtitlesToggle.checked = false;
    subtitlesToggle.disabled = true;

    video.classList.add('gray-screen');
    document.getElementById('output').classList.add('hidden-text');
    cameraIcon.classList.add('inactive');
    subtitlesIcon.classList.add('inactive');
});

let lastDetectedWord = '';

function updateDetectedWords(newWord) {
    const detectedWordsElement = document.getElementById('detected-words');
    let currentWords = detectedWordsElement.textContent.trim();

    // Split the current words into an array
    let wordsArray = currentWords.split(', ').filter(word => word.trim() !== '');

    // Add the new word to the array
    wordsArray.push(newWord);

    // Join the array into a string with a comma separator
    currentWords = wordsArray.join(', ');

    // Update the detected words element
    detectedWordsElement.textContent = currentWords;

    // Check if the array length is greater than 4
    if (wordsArray.length > 4) {
        // Wait for 1 second before removing the oldest word
        setTimeout(() => {
            // Remove the oldest word (the first one)
            wordsArray.shift();

            // Join the array back into a string
            currentWords = wordsArray.join(', ');

            // Update the detected words element with the trimmed list of words (limited to 4)
            detectedWordsElement.textContent = currentWords;
        }, 1000); // 1000 milliseconds = 1 second
    }
}



function captureFrame() {
    const video = document.getElementById('video');

    if (!video.srcObject) {
        return; // Exit if video stream is not available
    }

    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const dataUrl = canvas.toDataURL('image/jpeg');

    fetch('/process_frame', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({data_url: dataUrl})
    })
        .then(response => response.json())
        .then(data => {
            if (data.detected_action && data.detected_action !== lastDetectedWord) {
                //updateDetectedWords(data.detected_action.trim()); //TODO: To zakomentowac jesli nie ma dzialac nasz model
                //lastDetectedWord = data.detected_action.trim(); //TODO: To też
                console.log("INFO", "Mock")
            }
            setTimeout(captureFrame, 33.34); // Capture a frame approximately every 33ms for 30fps
        })
        .catch(error => {
            console.error('Error processing frame:', error);
            setTimeout(captureFrame, 33.34); // Continue capturing frames even if there's an error
        });
}

function generateSentence() {
    const detectedWordsElement = document.getElementById('detected-words');
    const detectedWordsText = detectedWordsElement.textContent;
    // Only generate a sentence if there are at least two words detected

    const words = detectedWordsText.split(', ').slice(-2);

    if (words.length < 2) {
        return;
    }

    fetch('/generate_sentence', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({words: words})
    })
        .then(response => response.json())
        .then(data => {
            const output = document.getElementById('output');
            output.textContent = data.sentence;
        })
        .catch(error => console.error('Error generating sentence:', error));
}

document.addEventListener('keydown', function (event) {
    const key = event.key.toUpperCase(); // Get the pressed key in uppercase
    let newWord = '';

    // Determine the word associated with the pressed key
    switch (key) {
        case 'T':
            newWord = 'Telefon';
            break;
        case 'P':
            newWord = 'Pomoc';
            break;
        case 'L':
            newWord = 'Lekarstwo';
            break;
        case 'A':
            newWord = 'Pogotowie';
            break;
        case 'Z':
            newWord = 'Zawal';
            break;
        case 'D':
            newWord = 'Lekarz';
            break;
        case 'N':
            newWord = 'Potrzebowac';
            break;
        case 'F':
            newWord = 'Pozar';
            break;
        case 'H':
            newWord = 'Szpital';
            break;
        case 'B':
            newWord = 'Bol';
            break;
        default:
            return; // Exit if key doesn't match any of the cases
    }

    // Update the detected words element with the new word
    updateDetectedWords(newWord);
});


// Call generateSentence function every time detected words are updated
const detectedWordsElement = document.getElementById('detected-words');
const observer = new MutationObserver(generateSentence);
observer.observe(detectedWordsElement, {childList: true, subtree: true});

