import cv2
import numpy as np
import base64
import mediapipe as mp
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Bidirectional, Input
from google.cloud import aiplatform

mp_holistic = mp.solutions.holistic  # Holistic model
mp_drawing = mp.solutions.drawing_utils  # Drawing utilities
holistic = mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
actions = np.array(
    ['Potrzebowac', 'Pozar', 'Zatrucie', 'Szpital', 'Telefon', 'Lekarstwo', 'Bol', 'Lekarz', 'Pogotowie', 'Zawal'])


PROJECT_NUMBER = "745796643"
ENDPOINT_ID = "6890214959783870464"


def predict_custom_trained_model(instances, project_number, endpoint_id):
    """Uses Vertex AI endpoint to make predictions."""
    endpoint = aiplatform.Endpoint(
        endpoint_name=f"projects/{project_number}/locations/us-central1/endpoints/{endpoint_id}"
    )
    result = endpoint.predict(instances=[instances])
    return result.predictions

def load_my_model(model_file):
    model = Sequential(
        [
            Input(shape=(30, 150)),
            Bidirectional(LSTM(64, return_sequences=True, activation='relu')),
            Dropout(0.1),
            Bidirectional(LSTM(128, return_sequences=True, activation='relu')),
            Dropout(0.1),
            Bidirectional(LSTM(64, return_sequences=False, activation='relu')),
            Dropout(0.1),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(actions.shape[0], activation='softmax')
        ]
    )
    model.load_weights(model_file)
    return model


class GestureRecognizer:
    def __init__(self):
        self.sequence = []
        self.sentence = []
        self.threshold = 0.90
        self.model = load_my_model('model_bi.h5')

    def mediapipe_detection(self, image, model):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # COLOR CONVERSION BGR 2 RGB
        image.flags.writeable = False  # Image is no longer writeable
        results = model.process(image)  # Make prediction
        image.flags.writeable = True  # Image is now writeable
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # COLOR COVERSION RGB 2 BGR
        return image, results

    def extract_keypoints(self, results):
        pose_landmarks = results.pose_landmarks.landmark if results.pose_landmarks else []
        if len(pose_landmarks) != 0:
            selected_landmarks = [pose_landmarks[i] for i in [0, 5, 2] + list(range(11, 17))]
            pose = np.array([[lm.x, lm.y, lm.z, lm.visibility] for lm in selected_landmarks]).flatten()
        else:
            pose = np.zeros(9 * 4)

        lh_landmarks = results.left_hand_landmarks.landmark if results.left_hand_landmarks else []
        if len(lh_landmarks) != 0:
            lh_selected = [lh_landmarks[i] for i in list(range(0, 9)) + list(range(10, 13)) + list(range(14, 21))]
            lh = np.array([[res.x, res.y, res.z] for res in lh_selected]).flatten()
        else:
            lh = np.zeros(19 * 3)

        rh_landmarks = results.right_hand_landmarks.landmark if results.right_hand_landmarks else []
        if len(rh_landmarks) != 0:
            rh_selected = [rh_landmarks[i] for i in list(range(0, 9)) + list(range(10, 13)) + list(range(14, 21))]
            rh = np.array([[res.x, res.y, res.z] for res in rh_selected]).flatten()
        else:
            rh = np.zeros(19 * 3)

        # Concatenate all landmark arrays
        return np.concatenate([pose, lh, rh])

    def process_video(self, data_url):
        img_data = data_url.split(",")[1]
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Process the frame using your existing logic
        image, results = self.mediapipe_detection(frame, holistic)

        keypoints = self.extract_keypoints(results)
        self.sequence.append(keypoints)
        self.sequence = self.sequence[-30:]

        if len(self.sequence) == 30:
            res = self.model.predict(np.expand_dims(self.sequence, axis=0))[0]

            if res[np.argmax(res)] > self.threshold:
                detected_action = actions[np.argmax(res)]
                if len(self.sentence) > 0:
                    if detected_action != self.sentence[-1]:
                        self.sentence.append(detected_action)
                else:
                    self.sentence.append(detected_action)

                return {'detected_action': detected_action, 'sentence': ' '.join(self.sentence)}

        return {'detected_action': None, 'sentence': ''}
