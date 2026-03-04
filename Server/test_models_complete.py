import cv2
import numpy as np
import onnxruntime as ort
import time
import os

print("=" * 60)
print("🔬 MOBILENET SSD + MOBILEFACENET (WORKING)")
print("=" * 60)

print("\n📥 Loading models...")

# MobileNet SSD for face detection
detector = cv2.dnn.readNetFromCaffe(
    "models/deploy.prototxt", "models/res10_300x300_ssd_iter_140000.caffemodel"
)
print("✅ MobileNet SSD loaded successfully!")

# MobileFaceNet for recognition
model_path = "MobileFaceNet/weights/mobilefacenet.onnx"

if not os.path.exists(model_path):
    print(f"❌ Model not found: {model_path}")
    print("   Please check the path")
    exit(1)

try:
    session = ort.InferenceSession(model_path)
    print("✅ MobileFaceNet loaded successfully!")

    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    input_shape = session.get_inputs()[0].shape

    print(f"   Input shape: {input_shape}")
    print(f"   Output shape: {session.get_outputs()[0].shape}")
    print(f"   Input name: {input_name}")
    print(f"   Output name: {output_name}")

    input_size = 112

except Exception as e:
    print(f"❌ Failed to load MobileFaceNet: {e}")
    exit(1)

print("\n📚 Initializing face database...")
known_faces = []
known_names = []


def preprocess_face(face_img):
    # Resize to 112x112
    face_resized = cv2.resize(face_img, (112, 112))

    # Convert BGR to RGB
    face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB)

    # Convert to float32
    face_float = face_rgb.astype(np.float32)

    # Apply: (x - 127.5) / 127.5
    face_normalized = (face_float - 127.5) / 127.5

    # Change from HWC to CHW (Height, Width, Channel) -> (Channel, Height, Width)
    face_chw = np.transpose(face_normalized, (2, 0, 1))

    # Add batch dimension (1, 3, 112, 112)
    face_input = np.expand_dims(face_chw, axis=0)

    return face_input.astype(np.float32)


def preprocess_face_cpp_compatible(face_img):
    # Resize to 112x112
    face_resized = cv2.resize(face_img, (112, 112))

    # Create blob
    # blobFromImage(image, scalefactor, size, mean, swapRB, crop)
    blob = cv2.dnn.blobFromImage(
        face_resized,  # input image
        1.0 / 127.5,  # scalefactor (1/127.5)
        (112, 112),  # size
        127.5,  # mean (127.5 for all channels)
        True,  # swapRB
        False,  # crop
        cv2.CV_32F,  # dtype
    )

    return blob


def get_face_embedding(face_img, use_cpp_method=True):
    if use_cpp_method:
        input_data = preprocess_face_cpp_compatible(face_img)
    else:
        input_data = preprocess_face(face_img)

    # Run inference
    outputs = session.run([output_name], {input_name: input_data})
    embedding = outputs[0].flatten()

    # L2 Normalization
    norm = np.linalg.norm(embedding)
    if norm > 1e-10:
        embedding = embedding / norm

    return embedding


def get_similarity(emb1, emb2):
    return float(np.dot(emb1, emb2))


def add_face_to_database(face_img, name, use_cpp_method=True):
    """Add new face to database"""
    embedding = get_face_embedding(face_img, use_cpp_method)
    known_faces.append(embedding)
    known_names.append(name)
    print(f"   ✅ Face added: {name}")
    return True


def recognize_face(face_img, threshold=0.35, use_cpp_method=True):
    """
    Recognize face from database
    """
    if len(known_faces) == 0:
        return "Unknown", 0.0

    current_emb = get_face_embedding(face_img, use_cpp_method)

    best_match = -1
    best_similarity = -1.0

    for i, known_emb in enumerate(known_faces):
        similarity = get_similarity(current_emb, known_emb)
        print(f"   Similarity with {known_names[i]}: {similarity:.4f}")
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = i
    if best_similarity > threshold:
        return known_names[best_match], best_similarity
    return "Unknown", best_similarity


# Test function to verify preprocessing is identical
def test_preprocessing_consistency():
    print("\n🔍 Testing preprocessing consistency...")
    # Create a test image with known values
    test_img = np.ones((200, 200, 3), dtype=np.uint8) * 128
    # Method 1: Custom preprocessing
    custom_result = preprocess_face(test_img)
    cpp_result = preprocess_face_cpp_compatible(test_img)
    print(f"   Custom preprocessing shape: {custom_result.shape}")
    print(f"   compatible shape: {cpp_result.shape}")
    print(f"   Mean difference: {np.mean(np.abs(custom_result - cpp_result)):.6f}")

    # Get embedding using both methods to compare
    emb_custom = get_face_embedding(test_img, use_cpp_method=False)
    emb_cpp = get_face_embedding(test_img, use_cpp_method=True)

    similarity = get_similarity(emb_custom, emb_cpp)
    print(f"   Embedding similarity: {similarity:.6f}")

    if similarity > 0.99:
        print("   ✅ Both methods produce VERY similar embeddings")
    else:
        print("   ⚠️ Warning: Methods produce different embeddings")

    print()


# Run the test
test_preprocessing_consistency()

print("\n📸 Opening camera...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("   Trying camera 1...")
    cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("❌ No camera found!")
    exit(1)
print("✅ Camera ready!")

print("\n🎯 Instructions:")
print("   - Press '1' to use C++ preprocessing method")
print("   - Press '2' to use custom preprocessing method")
print("   - Press 's' to save current face to database")
print("   - Press 'c' to clear database")
print("   - Press 'q' to quit")
print("=" * 60)

use_cpp_method = True

fps_counter = 0
fps_start_time = time.time()
fps = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to grab frame")
        break

    h, w = frame.shape[:2]
    display_frame = frame.copy()

    # Face detection using MobileNet SSD
    blob = cv2.dnn.blobFromImage(
        cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
    )
    detector.setInput(blob)
    detections = detector.forward()

    face_count = 0

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]

        if confidence > 0.6:
            face_count += 1

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x1, y1, x2, y2) = box.astype("int")

            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            face = frame[y1:y2, x1:x2]

            if face.size > 0 and face.shape[0] >= 50 and face.shape[1] >= 50:
                try:
                    name, similarity = recognize_face(
                        face, use_cpp_method=use_cpp_method
                    )

                    if name != "Unknown":
                        color = (0, 255, 0)
                    else:
                        color = (0, 0, 255)

                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)

                    label = f"{name} ({confidence:.2f})"
                    if name != "Unknown":
                        label += f" [{similarity:.3f}]"

                    (label_w, label_h), _ = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
                    )
                    cv2.rectangle(
                        display_frame, (x1, y1 - 25), (x1 + label_w, y1), color, -1
                    )
                    cv2.putText(
                        display_frame,
                        label,
                        (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        2,
                    )
                except Exception as e:
                    cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    cv2.putText(
                        display_frame,
                        "Error",
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 255),
                        2,
                    )

    # FPS calculation
    fps_counter += 1
    if time.time() - fps_start_time >= 1.0:
        fps = fps_counter
        fps_counter = 0
        fps_start_time = time.time()

    # Display info
    cv2.putText(
        display_frame,
        f"FPS: {fps}",
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2,
    )

    cv2.putText(
        display_frame,
        f"Faces detected: {face_count}",
        (10, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2,
    )

    cv2.putText(
        display_frame,
        f"Database: {len(known_faces)} faces",
        (10, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 0),
        2,
    )

    # Show current preprocessing method
    method_text = "C++ Method" if use_cpp_method else "Custom Method"
    method_color = (0, 255, 0) if use_cpp_method else (0, 165, 255)
    cv2.putText(
        display_frame,
        f"Method: {method_text}",
        (10, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        method_color,
        2,
    )

    if len(known_names) > 0:
        cv2.putText(
            display_frame,
            f"Last added: {known_names[-1]}",
            (10, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

    cv2.putText(
        display_frame,
        "1:C++ Method | 2:Custom | s:save | c:clear | q:quit",
        (10, h - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 255, 255),
        1,
    )

    cv2.imshow("MobileNet SSD + MobileFaceNet", display_frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        print("\n👋 Quitting...")
        break

    elif key == ord("1"):
        use_cpp_method = True
        print("\n✅ Switched to C++ preprocessing method")

    elif key == ord("2"):
        use_cpp_method = False
        print("\n✅ Switched to Custom preprocessing method")

    elif key == ord("s"):
        # Find the best face to save
        best_face = None
        best_conf = 0
        best_box = None

        for i in range(detections.shape[2]):
            conf = detections[0, 0, i, 2]
            if conf > 0.7 and conf > best_conf:
                best_conf = conf
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                best_box = box.astype("int")
                best_face = frame[best_box[1] : best_box[3], best_box[0] : best_box[2]]

        if best_face is not None and best_face.size > 0:
            name = input("\n📝 Enter name for this face: ").strip()
            if name:
                add_face_to_database(best_face, name, use_cpp_method)

                cv2.imshow("Saved Face", cv2.resize(best_face, (200, 200)))
                cv2.waitKey(500)
                cv2.destroyWindow("Saved Face")
        else:
            print("❌ No clear face detected (try again)")

    elif key == ord("c"):
        known_faces.clear()
        known_names.clear()
        print("\n✅ Database cleared!")

cap.release()
cv2.destroyAllWindows()

print("\n📊 Database Summary:")
if len(known_names) > 0:
    for i, name in enumerate(known_names):
        print(f"   {i+1}. {name}")
else:
    print("   No faces saved")
print("=" * 60)
