from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return FileResponse(
        path="(Airi Kanna) _ .mp4",
        filename="(Airi Kanna) _ .mp4",
        media_type='application/octet-stream'
    )

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, access_log=False)