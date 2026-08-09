import os, base64, time, uuid, pathlib, mimetypes
import httpx
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("MODEL", "veo-3.1-fast-generate-preview")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8000").rstrip("/")
BASE = "https://generativelanguage.googleapis.com/v1beta"

app = FastAPI(title="Image to Video Gemini Backend")
OUT = pathlib.Path("generated")
OUT.mkdir(exist_ok=True)
app.mount("/videos", StaticFiles(directory=str(OUT)), name="videos")

@app.get("/health")
def health():
    return {"ok": True, "model": MODEL}

@app.post("/generate")
async def generate(
    image: UploadFile = File(...),
    prompt: str = Form(...),
    duration: str = Form("8"),
    aspect_ratio: str = Form("9:16"),
):
    if not API_KEY:
        raise HTTPException(500, "GEMINI_API_KEY belum diatur di server.")
    if duration not in {"4","6","8"}:
        raise HTTPException(400, "Durasi harus 4, 6, atau 8 detik.")
    if aspect_ratio not in {"9:16","16:9"}:
        raise HTTPException(400, "aspect_ratio harus 9:16 atau 16:9.")

    raw = await image.read()
    if len(raw) > 20 * 1024 * 1024:
        raise HTTPException(400, "Gambar terlalu besar (maksimal 20 MB).")

    mime = image.content_type or mimetypes.guess_type(image.filename or "")[0] or "image/jpeg"
    image_b64 = base64.b64encode(raw).decode("ascii")

    payload = {
        "instances": [{
            "prompt": prompt,
            "image": {"inlineData": {"mimeType": mime, "data": image_b64}}
        }],
        "parameters": {
            "aspectRatio": aspect_ratio,
            "durationSeconds": duration,
            "resolution": "720p",
            "personGeneration": "allow_adult"
        }
    }

    headers = {"x-goog-api-key": API_KEY, "Content-Type": "application/json"}

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            f"{BASE}/models/{MODEL}:predictLongRunning",
            headers=headers, json=payload
        )
        if r.status_code >= 400:
            raise HTTPException(r.status_code, r.text)
        operation = r.json()
        name = operation.get("name")
        if not name:
            raise HTTPException(502, f"Operasi tidak ditemukan: {operation}")

        # Veo generation is asynchronous. Poll until done.
        for _ in range(90):  # ~15 minutes max
            await __import__("asyncio").sleep(10)
            s = await client.get(f"{BASE}/{name}", headers={"x-goog-api-key": API_KEY})
            if s.status_code >= 400:
                raise HTTPException(s.status_code, s.text)
            data = s.json()
            if data.get("done"):
                if "error" in data:
                    raise HTTPException(502, str(data["error"]))
                try:
                    video_uri = data["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
                except (KeyError, IndexError, TypeError):
                    raise HTTPException(502, f"Format hasil tidak dikenali: {data}")

                vr = await client.get(video_uri, headers={"x-goog-api-key": API_KEY})
                if vr.status_code >= 400:
                    raise HTTPException(vr.status_code, vr.text)

                filename = f"{uuid.uuid4().hex}.mp4"
                path = OUT / filename
                path.write_bytes(vr.content)
                return {
                    "status": "done",
                    "videoUrl": f"{PUBLIC_BASE_URL}/videos/{filename}"
                }

        raise HTTPException(504, "Pembuatan video terlalu lama. Coba lagi.")

# Run:
# uvicorn main:app --host 0.0.0.0 --port 8000
