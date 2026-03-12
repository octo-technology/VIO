from fastapi import FastAPI
from fastapi.responses import FileResponse
from picamera2 import Picamera2
from picamera2.outputs import FfmpegOutput
import os

app = FastAPI()

# Répertoire pour les fichiers HLS
HLS_DIR = "/home/bapo/hls"
os.makedirs(HLS_DIR, exist_ok=True)

# Initialiser Picamera2
picam2 = Picamera2()
camera_config = picam2.create_video_configuration(main={"size": (1280, 720)})
picam2.configure(camera_config)

# Configurer FfmpegOutput pour générer le flux HLS
hls_output = FfmpegOutput(
    f"{HLS_DIR}/stream.m3u8",
    audio=False,
    fmt="hls",
    options={
        "hls_time": 2,
        "hls_list_size": 3,
        "hls_flags": "delete_segments"
    }
)

@app.on_event("startup")
def startup_event():
    """Démarre la caméra et le flux HLS au démarrage du serveur."""
    picam2.start_recording(hls_output)

@app.get("/camera/stream.m3u8")
def get_hls_playlist():
    """Serve la playlist HLS."""
    return FileResponse(f"{HLS_DIR}/stream.m3u8")

@app.get("/camera/{segment}")
def get_hls_segment(segment: str):
    """Serve les segments HLS."""
    segment_path = os.path.join(HLS_DIR, segment)
    if os.path.exists(segment_path):
        return FileResponse(segment_path)
    return {"error": "Segment not found"}

@app.on_event("shutdown")
def shutdown_event():
    """Arrête la caméra proprement lors de l'arrêt du serveur."""
    picam2.stop_recording()
    picam2.close()
