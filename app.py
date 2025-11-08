from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from yt_dlp import YoutubeDL
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os

ytoptions = {
    "quiet": True,
    "no_warnings": True,
    "format": "bestvideo+bestaudio/best",
    "outtmpl": "%(title)s",
    "merge_output_format": "mkv",
}


def human_readable_size(size: int, decimal_places: int = 2) -> str:
    """Convert bytes to human readable size"""
    size_float = float(size)
    for unit in ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]:
        if size_float < 1024.0 or unit == "PiB":
            break
        size_float /= 1024.0
    return f"{size_float:.{decimal_places}f} {unit}"


class ExtractRequest(BaseModel):
    url: str


class ExtractResponse(BaseModel):
    title: Optional[str] = None
    formats: List[Dict[str, Any]] = []
    error: Optional[str] = None


app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    """Serve the main HTML file"""
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    index_file = os.path.join(static_dir, "index.html")
    return FileResponse(index_file)


@app.get("/api/extract")
async def extract(url: str):
    """Extract YouTube video information"""
    try:
        with YoutubeDL(ytoptions) as ydl:
            ie = ydl.get_info_extractor("Youtube")
            if not ie.suitable(url):
                return JSONResponse(
                    status_code=400, content={"error": "Unsupported URL"}
                )

            info = ie.extract(url)

            # Format the response
            formats = []
            for fmt in info.get("formats", []):
                formats.append(
                    {
                        "filesize": fmt.get("filesize"),
                        "format_note": fmt.get("format_note", "N/A"),
                        "fps": fmt.get("fps"),
                        "ext": fmt.get("ext", "N/A"),
                        "vcodec": fmt.get("vcodec", "N/A"),
                        "acodec": fmt.get("acodec", "N/A"),
                        "url": fmt.get("url", ""),
                        "filesize_readable": (
                            human_readable_size(fmt.get("filesize"))
                            if fmt.get("filesize")
                            else "N/A"
                        ),
                    }
                )

            return {"title": info.get("title"), "formats": formats, "error": None}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
