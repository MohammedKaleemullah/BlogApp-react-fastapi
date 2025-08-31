from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services import ServiceManager
from routes import router, set_service_manager

import uvicorn


app = FastAPI(title="Combined RAG + Image API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service_manager = ServiceManager()
set_service_manager(service_manager)

app.include_router(router)


# Startup and shutdown events
@app.on_event("startup")
async def startup():
    print("🚀 FastAPI server starting...")
    try:
        success = service_manager.initialize_all()
        if success:
            print("✅ All services ready!")
        else:
            print("⚠️ Some services failed to initialize - continuing with limited functionality")
    except Exception as e:
        print(f"⚠️ Service initialization error: {e}")
        print("Continuing with basic server functionality...")

@app.on_event("shutdown") 
async def shutdown():
    service_manager.cleanup()

if __name__ == "__main__":
    
    print("🚀 Starting server on port 8005...")
    uvicorn.run("main:app", host="0.0.0.0", port=8005, reload=True)
    print("Server stopped.")