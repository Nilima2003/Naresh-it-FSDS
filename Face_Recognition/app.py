import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated as an API")

from flask import Flask, render_template, request, redirect, url_for
import os
import cv2
import face_recognition
import numpy as np

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Step 1: Load known faces
def load_known_faces(known_folder):
    known_encodings = []
    known_names = []
    for filename in os.listdir(known_folder):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            name = os.path.splitext(filename)[0]
            image_path = os.path.join(known_folder, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if len(encodings) > 0:
                known_encodings.append(encodings[0])
                known_names.append(name)
                print(f"Loaded {name}")
    return known_encodings, known_names

known_encodings, known_names = load_known_faces("known_people")

# Step 2: Detect faces from uploaded image
def recognize_faces(image_path):
    frame = cv2.imread(image_path)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb)
    face_encodings = face_recognition.face_encodings(rgb, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
        name = "Unknown"

        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_names[best_match_index]

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 25), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.jpg')
    cv2.imwrite(output_path, frame)
    return output_path

# Step 3: Frontend routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return redirect(url_for('index'))
    file = request.files['image']
    if file.filename == '':
        return redirect(url_for('index'))
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    result_path = recognize_faces(file_path)
    return render_template('index.html', uploaded_image=file_path, result_image=result_path)

if __name__ == '__main__':
    app.run(debug=True)
