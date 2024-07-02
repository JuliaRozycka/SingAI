# AI translator for Polish Sign Language in emergency situations.

## Dataset
The dataset was created by us especialy for this project. It consist of 11 clases (11 moves), 200 instances each. One instance cosisist od 30 frames of keypoints detected from the body through Mediapipe API.
<img width="732" alt="image" src="https://github.com/JuliaRozycka/SingAI/assets/92980605/441ce13d-5c8e-45b9-8a7a-1d22be621067">

## Model
Model that had the best performance consist of 3 BiLSTM layers and Dropout layers:
<img width="843" alt="image" src="https://github.com/JuliaRozycka/SingAI/assets/92980605/fc752266-de3e-4d11-9a42-3af09a861968">

## GUI
The application was created using Flask. Moreover we decided to introduce "live subtitles" using Ollama with model Llama-3B to create sentences from single words.
<img width="1204" alt="image" src="https://github.com/JuliaRozycka/SingAI/assets/92980605/ea724657-1669-499f-a312-0c5373e773c5">


