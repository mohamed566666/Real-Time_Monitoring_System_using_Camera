"""
test_models_realistic.py
========================
Live camera test that uses the EXACT same FaceEngine class the server uses.
No separate preprocessing, no separate threshold — everything is identical
to what happens when the API receives an image.

Controls
--------
  s       → save current face to in-memory DB (will prompt for a name)
  d       → toggle debug overlay (similarity scores for every DB entry)
  c       → clear in-memory DB
  t +/-   → raise / lower threshold by 0.01 on the fly
  q       → quit
"""

import sys
import os
import time
import cv2
import numpy as np

# ── make sure we can import FaceEngine regardless of where we run from ──────
_server_root = os.path.abspath(os.path.dirname(__file__))  # Server/
sys.path.insert(0, os.path.join(_server_root, "app"))  # Server/app/
from app.infrastructure.aiModels.face_engine import FaceEngine

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CAMERA_INDEX = 0
DETECTION_CONF = 0.7  # minimum detector confidence to draw a box
INITIAL_THRESHOLD = 0.60  # starting recognition threshold (same as server default)
THRESHOLD_STEP = 0.01


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def draw_text_with_bg(
    frame, text, pos, font_scale=0.55, thickness=1, fg=(255, 255, 255), bg=(0, 0, 0)
):
    (tw, th), bl = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
    )
    x, y = pos
    cv2.rectangle(frame, (x, y - th - bl - 2), (x + tw + 4, y + bl), bg, -1)
    cv2.putText(
        frame,
        text,
        (x + 2, y - 1),
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        fg,
        thickness,
        cv2.LINE_AA,
    )


def color_for_similarity(sim: float, threshold: float):
    """Green if match, red if not, yellow if close (within 0.05 of threshold)."""
    if sim >= threshold:
        return (0, 200, 0)
    if sim >= threshold - 0.05:
        return (0, 200, 255)
    return (0, 0, 220)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("Loading FaceEngine (same class as the server)...")
    engine = FaceEngine(recognition_threshold=INITIAL_THRESHOLD)
    threshold = INITIAL_THRESHOLD
    print(f"  threshold = {threshold:.2f}")

    # in-memory face DB:  list of {"name": str, "embedding": List[float]}
    db: list[dict] = []
    show_debug = False

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("No camera found.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    print("\nCamera ready.")
    print("  s        save face to DB")
    print("  d        toggle debug overlay")
    print("  c        clear DB")
    print("  t+ / t-  raise / lower threshold")
    print("  q        quit\n")

    fps_t = time.time()
    fps_cnt = 0
    fps = 0.0

    # keep last detections so 's' can grab the best face without re-detecting
    last_detections = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        h, w = frame.shape[:2]

        # ── face detection (same call as detect_all_faces) ────────────────
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)
        )
        engine.detector.setInput(blob)
        raw = engine.detector.forward()

        last_detections = []
        for i in range(raw.shape[2]):
            conf = float(raw[0, 0, i, 2])
            if conf < DETECTION_CONF:
                continue
            box = raw[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype("int")
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            face_crop = frame[y1:y2, x1:x2]
            if (
                face_crop.size == 0
                or face_crop.shape[0] < 40
                or face_crop.shape[1] < 40
            ):
                continue
            last_detections.append(
                {"face": face_crop, "conf": conf, "box": (x1, y1, x2, y2)}
            )

        # ── recognition ───────────────────────────────────────────────────
        for det in last_detections:
            face_crop = det["face"]
            x1, y1, x2, y2 = det["box"]

            # get embedding using the EXACT same pipeline as the server
            embedding = engine.get_embedding(face_crop)

            best_name = "Unknown"
            best_sim = -1.0
            all_sims = []

            for entry in db:
                sim = engine.calculate_similarity(embedding, entry["embedding"])
                all_sims.append((entry["name"], sim))
                if sim > best_sim:
                    best_sim = sim
                    best_name = entry["name"] if sim >= threshold else "Unknown"

            box_color = (
                color_for_similarity(best_sim, threshold) if db else (200, 200, 0)
            )
            cv2.rectangle(display, (x1, y1), (x2, y2), box_color, 2)

            # main label
            if db:
                label = f"{best_name}  {best_sim:.3f}" if best_sim >= 0 else "Unknown"
            else:
                label = f"det:{det['conf']:.2f}"
            draw_text_with_bg(
                display, label, (x1, y1 - 4), fg=(255, 255, 255), bg=box_color
            )

            # debug overlay: show similarity against every DB entry
            if show_debug and all_sims:
                for idx, (name, sim) in enumerate(all_sims):
                    c = color_for_similarity(sim, threshold)
                    draw_text_with_bg(
                        display,
                        f"{name}: {sim:.3f}",
                        (x1 + 2, y2 + 18 + idx * 20),
                        font_scale=0.45,
                        fg=(255, 255, 255),
                        bg=c,
                    )

        # ── HUD ───────────────────────────────────────────────────────────
        fps_cnt += 1
        if time.time() - fps_t >= 1.0:
            fps = fps_cnt / (time.time() - fps_t)
            fps_cnt = 0
            fps_t = time.time()

        hud_lines = [
            f"FPS: {fps:.1f}",
            f"Threshold: {threshold:.2f}  (t+ / t-)",
            f"DB: {len(db)} face(s)   (s=save  c=clear)",
            f"Debug overlay: {'ON' if show_debug else 'OFF'}  (d)",
            f"Faces detected: {len(last_detections)}",
        ]
        for i, line in enumerate(hud_lines):
            draw_text_with_bg(
                display,
                line,
                (10, 28 + i * 26),
                font_scale=0.6,
                fg=(255, 255, 0),
                bg=(30, 30, 30),
            )

        # threshold bar: visual representation 0.0 → 1.0
        bar_x, bar_y, bar_w, bar_h = 10, h - 30, 300, 14
        cv2.rectangle(
            display, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (50, 50, 50), -1
        )
        filled = int(bar_w * threshold)
        cv2.rectangle(
            display, (bar_x, bar_y), (bar_x + filled, bar_y + bar_h), (0, 200, 100), -1
        )
        cv2.rectangle(
            display, (bar_x, bar_y), (bar_x + bar_w, bar_y + bar_h), (150, 150, 150), 1
        )
        draw_text_with_bg(
            display,
            f"thr={threshold:.2f}",
            (bar_x + bar_w + 8, bar_y + bar_h - 1),
            font_scale=0.45,
        )

        cv2.imshow("FaceEngine — Realistic Test", display)

        # ── key handling ─────────────────────────────────────────────────
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

        elif key == ord("d"):
            show_debug = not show_debug
            print(f"Debug overlay: {'ON' if show_debug else 'OFF'}")

        elif key == ord("c"):
            db.clear()
            print("DB cleared.")

        elif key == ord("t"):
            # next keypress determines + or -
            print("Press '+' to raise threshold or '-' to lower it:")
            k2 = cv2.waitKey(3000) & 0xFF
            if k2 == ord("+"):
                threshold = min(1.0, round(threshold + THRESHOLD_STEP, 2))
            elif k2 == ord("-"):
                threshold = max(0.0, round(threshold - THRESHOLD_STEP, 2))
            engine.threshold = threshold
            print(f"Threshold → {threshold:.2f}")

        elif key == ord("s"):
            # find highest-confidence face in last frame
            if not last_detections:
                print("No face detected — move closer to the camera.")
                continue

            best = max(last_detections, key=lambda d: d["conf"])
            face_crop = best["face"]

            # show a preview
            preview = cv2.resize(face_crop, (200, 200))
            cv2.imshow("Save this face?", preview)
            cv2.waitKey(500)
            cv2.destroyWindow("Save this face?")

            name = input("Enter name (leave blank to cancel): ").strip()
            if not name:
                print("Cancelled.")
                continue

            # use the SAME get_embedding pipeline as the server
            emb = engine.get_embedding(face_crop)
            db.append({"name": name, "embedding": emb})
            print(f"Saved '{name}'  (DB now has {len(db)} face(s))")

            # quick self-check: similarity of the just-saved face against itself
            self_sim = engine.calculate_similarity(emb, emb)
            print(f"  Self-similarity sanity check: {self_sim:.6f}  (should be ~1.0)")

    cap.release()
    cv2.destroyAllWindows()

    if db:
        print("\n── DB summary ──────────────────────────────")
        for i, e in enumerate(db):
            print(f"  {i+1}. {e['name']}")
        print("────────────────────────────────────────────")


if __name__ == "__main__":
    main()
