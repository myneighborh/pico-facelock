import cv2
import numpy as np
import tensorflow as tf
import firebase_admin
from firebase_admin import credentials, db


class CustomDepthwiseConv2D(tf.keras.layers.DepthwiseConv2D):
    def __init__(self, *args, **kwargs):
        kwargs.pop('groups', None)
        super().__init__(*args, **kwargs)

    def get_config(self):
        config = super().get_config()
        config.pop('groups', None)
        return config


def main():
    model_path = "/Users/hyun/git_ws/pico-facelock/face-recognition-doorlock/keras_model.h5"
    model = load_custom_model(model_path)
    class_names = ['Authorized', 'Unauthorized']

    key_path = "/Users/hyun/git_ws/pico-facelock/face-recognition-doorlock/firebase_config.json"
    db_url = "https://face-recognition-door-h-default-rtdb.firebaseio.com/"

    initialize_firebase(key_path, db_url)
    frame = capture_image()
    image = preprocess_image(frame)
    predict_and_upload(image, model, class_names)


def load_custom_model(model_path: str):
    return tf.keras.models.load_model(
        model_path,
        custom_objects={'DepthwiseConv2D': CustomDepthwiseConv2D}
    )


def capture_image():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam.")

    # Originally: capture on person detection → Now: replaced with spacebar
    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.imshow('Press Space to Capture', frame)
        if cv2.waitKey(1) & 0xFF == ord(' '):  # Space bar
            break

    cap.release()
    cv2.destroyAllWindows()
    return frame


def preprocess_image(image):
    img = cv2.resize(image, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_array = np.array(img) / 255.0
    return np.expand_dims(img_array, axis=0)


def initialize_firebase(key_path: str, db_url: str):
    if not firebase_admin._apps:
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred, {
            'databaseURL': db_url
        })


def predict_and_upload(image, model, class_names):
    predictions = model.predict(image)[0]
    predicted_index = int(np.argmax(predictions))
    predicted_label = class_names[predicted_index]
    confidence = float(predictions[predicted_index])

    db.reference('face_predictions').set({
        'label': predicted_label,
        'confidence': round(confidence, 4)
    })

    door_open_state = (predicted_index == 0)
    db.reference('door_open').set(door_open_state)

    print(f"Result: {predicted_label} ({confidence:.4f})")


if __name__ == "__main__":
    main()
