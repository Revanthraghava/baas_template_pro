from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
import traceback

app = FastAPI(title="BaaS Pro API")

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as exc:
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"message": str(exc), "detail": traceback.format_exc()},
        )

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(projects_router, prefix="/projects", tags=["Projects"])

@app.get("/")
def read_root():
    return {"message": "Welcome to BaaS Pro"}