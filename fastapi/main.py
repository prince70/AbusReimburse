import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import auth, records, audit, finance, base

logger = logging.getLogger(__name__)

api = FastAPI(title="报销管理系统 API", version="1.0.0")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://192.168.10.202:8083",
]


@api.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误", "error": str(exc)})


api.include_router(auth.router, prefix="/api/auth", tags=["认证"])
api.include_router(records.router, prefix="/api/v1", tags=["报销单"])
api.include_router(audit.router, prefix="/api/v1", tags=["审批"])
api.include_router(finance.router, prefix="/api/v1", tags=["财务"])
api.include_router(base.router, prefix="/api/v1", tags=["基础数据"])


@api.get("/")
def root():
    return {"message": "报销管理系统 API 运行中", "version": "1.0.0"}


app = CORSMiddleware(
    app=api,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
