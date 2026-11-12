"""PetGuard Gradio UI: configure, confirm, process, edit and reprocess without rerunning cells."""
from __future__ import annotations
import json
import subprocess
import uuid
from pathlib import Path

import cv2
import gradio as gr
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

from .main import process_video
from .zone import resize_frame, validate_polygon

BASE = Path("/content/PetGuard-AI") if Path("/content/PetGuard-AI").exists() else Path(__file__).resolve().parents[1]
RUNS = BASE / "results" / "runs"
RUNS.mkdir(parents=True, exist_ok=True)
WIDTH = 960
MAX_SECONDS = 60
MAX_MB = 250
MODE_LABELS = {
    "Floor or room area": "floor",
    "Sofa or furniture": "overlap",
}

def empty_state():
    return {"video": None, "frame": None, "size": None, "points": [],
            "saved": None, "mode": "Floor or room area", "dirty": False,
            "revision": 0, "result_revision": None}

def image_with_polygon(state):
    if state.get("frame") is None:
        return None
    image = Image.fromarray(state["frame"].copy())
    d = ImageDraw.Draw(image)
    pts = [tuple(p) for p in state["points"]]
    if len(pts) >= 2:
        d.line(pts, fill="#f44336", width=4)
    if len(pts) >= 3:
        d.line([pts[-1], pts[0]], fill="#f44336", width=3)
    for idx, (x, y) in enumerate(pts):
        d.ellipse((x-6, y-6, x+6, y+6), fill="#f44336", outline="white", width=2)
        d.text((x+8, y-15), str(idx+1), fill="white")
    return image

def load_video(path, state):
    state = empty_state()
    if not path:
        return state, None, "Upload an MP4 to begin.", None, None, None
    path = Path(path)
    if not path.exists():
        return state, None, "The uploaded file is missing.", None, None, None
    if path.stat().st_size > MAX_MB * 1024 * 1024:
        return state, None, f"Video exceeds {MAX_MB} MB. Please choose a smaller clip.", None, None, None
    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            return state, None, "Cannot open video. Use an MP4 encoded with H.264.", None, None, None
        fps = cap.get(cv2.CAP_PROP_FPS)
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if fps <= 0 or count <= 0:
            return state, None, "Cannot determine video duration.", None, None, None
        duration = count / fps
        if duration > MAX_SECONDS:
            return state, None, f"Video is {duration:.1f}s. Please trim it to {MAX_SECONDS}s or less.", None, None, None
        cap.set(cv2.CAP_PROP_POS_FRAMES, count // 2)
        ok, frame = cap.read()
        if not ok:
            return state, None, "Cannot read reference frame.", None, None, None
        frame = resize_frame(frame, WIDTH)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        state.update(video=str(path), frame=rgb, size=(rgb.shape[1], rgb.shape[0]))
        return state, image_with_polygon(state), f"Video ready ({duration:.1f}s). Click at least 3 corners, then Confirm.", None, None, None
    finally:
        cap.release()

def select_point(state, evt: gr.SelectData):
    state = dict(state)
    if state.get("frame") is None:
        return state, None, "Upload a video first."
    x, y = map(int, evt.index[:2])
    w, h = state["size"]
    if not (0 <= x < w and 0 <= y < h):
        return state, image_with_polygon(state), "Click inside the picture."
    state["points"] = [*state["points"], [x, y]]
    state["dirty"] = True
    return state, image_with_polygon(state), f"{len(state['points'])} corners selected. Confirm when ready."

def undo(state):
    state = dict(state)
    state["points"] = list(state["points"][:-1])
    state["dirty"] = True
    return state, image_with_polygon(state), "Last corner undone. Confirm to apply changes."

def redraw(state):
    state = dict(state)
    state["points"] = []
    state["dirty"] = True
    return state, image_with_polygon(state), "Click new corners. Your last confirmed zone is preserved until you Confirm."

def edit(state):
    state = dict(state)
    if state.get("saved"):
        state["points"] = [p[:] for p in state["saved"]["polygon"]]
        state["mode"] = state["saved"]["label"]
    state["dirty"] = True
    return state, image_with_polygon(state), state["mode"], "Editing draft. Confirm or Cancel."

def cancel(state):
    state = dict(state)
    saved = state.get("saved")
    if saved:
        state["points"] = [p[:] for p in saved["polygon"]]
        state["mode"] = saved["label"]
        state["dirty"] = False
        message = "Changes canceled; last confirmed zone restored."
    else:
        state["points"] = []
        state["dirty"] = False
        message = "Draft cleared. No confirmed zone yet."
    return state, image_with_polygon(state), state["mode"], message

def change_mode(mode, state):
    state = dict(state)
    state["mode"] = mode
    state["dirty"] = True
    return state, "Area type changed. Confirm to apply."

def confirm(state, mode):
    state = dict(state)
    if not state.get("video"):
        return state, "Upload a video first."
    pts = state["points"]
    if len(pts) < 3:
        return state, "Select at least 3 corners."
    try:
        validate_polygon(pts, state.get("size"))
    except ValueError as exc:
        return state, str(exc)
    state["mode"] = mode
    state["revision"] += 1
    state["saved"] = {"polygon": [p[:] for p in pts], "label": mode,
                      "zone_mode": MODE_LABELS[mode], "size": list(state["size"]),
                      "video_name": Path(state["video"]).name,
                      "revision": state["revision"]}
    state["dirty"] = False
    return state, f"✓ Zone confirmed (version {state['revision']}). Click Process Video when ready."

def confirm_and_clear(state, mode):
    state, message = confirm(state, mode)
    if message.startswith("✓"):
        return state, None, None, None, message + " Previous results cleared; reprocess to update."
    return state, gr.skip(), gr.skip(), gr.skip(), message

def run_processing(state, progress=gr.Progress()):
    if not state.get("video") or not state.get("saved"):
        return state, None, None, None, "Please upload a video and confirm a restricted area first."
    if state["dirty"]:
        return state, None, None, None, "You have unsaved changes. Confirm or Cancel before processing."
    config = state["saved"]
    if config["video_name"] != Path(state["video"]).name:
        return state, None, None, None, "The selected area belongs to another video."
    run_id = uuid.uuid4().hex[:12]
    folder = RUNS / run_id
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "zone_config.json").write_text(json.dumps(config, indent=2))
    output = folder / "annotated.mp4"
    csv_path = folder / "events.csv"
    progress(0.05, desc="Loading detector and processing video")
    try:
        summary = process_video(
            input_path=state["video"], output_path=output, event_csv=csv_path,
            polygon=config["polygon"], weights="yolov8s.pt", target_width=WIDTH,
            confidence=0.35, imgsz=960, mode=config["zone_mode"], confirm_frames=5
        )
        browser_mp4 = folder / "petguard_browser.mp4"
        command = ["ffmpeg", "-y", "-loglevel", "error", "-i", str(output),
                   "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(browser_mp4)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        state = dict(state)
        state["result_revision"] = state["revision"]
        progress(1.0, desc="Complete")
        return (state, str(browser_mp4), str(csv_path),
                str(summary["predictions_csv"]),
                f"Completed {summary['frames']} frames; {summary['events']} predicted events; "
                f"average {summary['avg_ms']} ms/frame; P95 {summary['p95_ms']} ms; "
                f"end-to-end {summary['end_to_end_fps']} FPS. Run ID: {run_id}. "
                "Verify alerts against ground truth.")
    except Exception as e:
        return state, None, None, None, f"Processing failed: {type(e).__name__}: {e}"

def build_app():
    with gr.Blocks(title="PetGuard AI — Restricted Zone Monitor") as app:
        gr.Markdown("# 🐾 PetGuard AI — Pet-free Area Monitor")
        gr.Markdown("Upload a **fixed-camera** video, choose an area pets should avoid, then process. "
                    "**Nothing runs until you click Process Video.** Maximum clip: 60 seconds / 250 MB.")
        state = gr.State(empty_state())
        video_file = gr.File(label="1. Upload video (MP4)", file_types=[".mp4"], type="filepath")
        mode = gr.Radio(list(MODE_LABELS), value="Floor or room area",
                        label="2. Where should pets not go?")
        preview = gr.Image(label="3. Click at least 3 corners around the restricted area",
                           type="pil", interactive=False, width=960)
        with gr.Row():
            edit_button = gr.Button("Edit zone")
            undo_button = gr.Button("Undo last corner")
            redraw_button = gr.Button("Redraw")
            cancel_button = gr.Button("Cancel edits")
            confirm_button = gr.Button("Confirm zone", variant="primary")
        status = gr.Textbox(label="Setup / processing status", interactive=False,
                            value="Upload a video to start.")
        process_button = gr.Button("▶ Process Video", variant="primary")
        # Keep the output video compact and centered; the source aspect ratio is preserved.
        with gr.Row():
            with gr.Column(scale=1, min_width=80):
                pass
            with gr.Column(scale=3, min_width=400):
                result_video = gr.Video(
                    label="Annotated Output",
                    width=750,
                    height=420,
                    show_download_button=True,
                    interactive=False,
                )
            with gr.Column(scale=1, min_width=80):
                pass
        with gr.Row():
            events_file = gr.File(label="Download event CSV")
            predictions_file = gr.File(label="Download frame predictions CSV")
        video_file.change(load_video, inputs=[video_file, state],
                          outputs=[state, preview, status, result_video, events_file, predictions_file])
        preview.select(select_point, inputs=[state], outputs=[state, preview, status])
        undo_button.click(undo, inputs=[state], outputs=[state, preview, status])
        redraw_button.click(redraw, inputs=[state], outputs=[state, preview, status])
        edit_button.click(edit, inputs=[state], outputs=[state, preview, mode, status])
        cancel_button.click(cancel, inputs=[state], outputs=[state, preview, mode, status])
        mode.change(change_mode, inputs=[mode, state], outputs=[state, status])
        confirm_button.click(confirm_and_clear, inputs=[state, mode],
                             outputs=[state, result_video, events_file, predictions_file, status])
        process_button.click(run_processing, inputs=[state],
                             outputs=[state, result_video, events_file, predictions_file, status],
                             concurrency_limit=1)
        gr.Markdown("**Limitations:** This prototype assumes a stationary camera. Furniture mode "
                    "uses 2D overlap, not confirmed physical occupancy. Human-as-dog false positives "
                    "remain possible; evaluate results with manually labeled data.")
    return app

if __name__ == "__main__":
    build_app().queue(default_concurrency_limit=1).launch(share=True, show_error=True)
