from fastapi import FastAPI
from app.routes.video_routes import router
import uvicorn
from fastapi import FastAPI
from app.routes.video_routes import router
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)