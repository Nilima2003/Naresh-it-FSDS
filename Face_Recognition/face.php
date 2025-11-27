<?php

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_FILES['image'])) {
    $uploadDir = __DIR__ . '/uploads/';
    if (!file_exists($uploadDir)) mkdir($uploadDir, 0777, true);

    $uploadFile = $uploadDir . basename($_FILES['image']['name']);
    move_uploaded_file($_FILES['image']['tmp_name'], $uploadFile);

    // Run Python script (inline code)
    $pythonCode = <<<PYTHON
import face_recognition, cv2, numpy as np, os, sys

known_folder = "known_people"
input_image = sys.argv[1]
output_image = sys.argv[2]

# Load known faces
known_encodings, known_names = [], []
for f in os.listdir(known_folder):
    if f.lower().endswith((".jpg", ".jpeg", ".png")):
        name = os.path.splitext(f)[0]
        img = face_recognition.load_image_file(os.path.join(known_folder, f))
        encs = face_recognition.face_encodings(img)
        if len(encs) > 0:
            known_encodings.append(encs[0])
            known_names.append(name)

frame = cv2.imread(input_image)
rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
faces = face_recognition.face_locations(rgb)
encs = face_recognition.face_encodings(rgb, faces)

for (top, right, bottom, left), enc in zip(faces, encs):
    matches = face_recognition.compare_faces(known_encodings, enc, tolerance=0.5)
    name = "Unknown"
    dist = face_recognition.face_distance(known_encodings, enc)
    if len(dist) > 0:
        i = np.argmin(dist)
        if matches[i]:
            name = known_names[i]
    cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
    cv2.rectangle(frame, (left, bottom-25), (right, bottom), (0,255,0), cv2.FILLED)
    cv2.putText(frame, name, (left+6, bottom-6), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,0), 4)

cv2.imwrite(output_image, frame)
PYTHON;

    // Save python script temporarily
    $pyFile = __DIR__ . '/temp_face_recognizer.py';
    file_put_contents($pyFile, $pythonCode);

    $outputFile = $uploadDir . 'result_' . basename($_FILES['image']['name']);

    // Execute Python
    $cmd = "python \"" . $pyFile . "\" \"" . $uploadFile . "\" \"" . $outputFile . "\"";
    exec($cmd, $out, $status);

    $uploadedPath = 'uploads/' . basename($_FILES['image']['name']);
    $resultPath = 'uploads/' . basename($outputFile);
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Face Recognition</title>
<style>
body { font-family: Arial; background: #f7f7f7; text-align: center; }
h2 { margin-top: 20px; color: #333; }
form { margin-top: 30px; }
input[type=file] { padding: 10px; }
input[type=submit] {
  padding: 10px 25px;
  background-color: #1f8883ff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}
.img-container { display: flex; justify-content: center; gap: 40px; margin-top: 30px; }
img { border: 2px solid #ccc; border-radius: 10px; width: 300px; }
</style>
</head>
<body>
  <h2>Face Recognition</h2>
  <form method="post" enctype="multipart/form-data">
    <input type="file" name="image" required>
    <input type="submit" value="Upload">
  </form>

  <?php if (!empty($uploadedPath)): ?>
  <div class="img-container">
    <div>
      <h3>Uploaded Image</h3>
      <img src="<?= htmlspecialchars($uploadedPath) ?>" alt="Uploaded">
    </div>
    <div>
      <h3>Result</h3>
      <img src="<?= htmlspecialchars($resultPath) ?>" alt="Result">
    </div>
  </div>
  <?php endif; ?>
</body>
</html>