import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from database import ensure_expense_reports_updated_at_column
from routers import auth, records, audit, finance, base

logger = logging.getLogger(__name__)

api = FastAPI(title="报销管理系统 API", version="1.0.0")

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://192.168.10.202:8083",
    "http://reimbursement.abushardware.com",
]

# 前端构建产物目录 (AbusReimburse\ABUS\dist)
frontend_dist = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ABUS", "dist"))


@api.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "服务器内部错误", "error": str(exc)})


@api.on_event("startup")
def ensure_schema():
    ensure_expense_reports_updated_at_column()


api.include_router(auth.router, prefix="/api/auth", tags=["认证"])
api.include_router(records.router, prefix="/api/v1", tags=["报销单"])
api.include_router(audit.router, prefix="/api/v1", tags=["审批"])
api.include_router(finance.router, prefix="/api/v1", tags=["财务"])
api.include_router(base.router, prefix="/api/v1", tags=["基础数据"])


@api.get("/")
def root():
    if os.path.isfile(os.path.join(frontend_dist, "index.html")):
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    return {"message": "报销管理系统 API 运行中", "version": "1.0.0"}


# ===================== 前端静态文件托管（生产环境，Vue history 模式回退） =====================
# 本项目后端路由自带 /api 前缀，前端请求同源直连，无需剥前缀中间件
# 注意：必须放在所有 API 路由之后注册，保证 /api/... 路由优先匹配
if os.path.isdir(frontend_dist):
    if os.path.isdir(os.path.join(frontend_dist, "assets")):
        api.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="frontend-assets")

    @api.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        candidate = os.path.realpath(os.path.join(frontend_dist, full_path))
        dist_real = os.path.realpath(frontend_dist)
        if full_path and candidate.startswith(dist_real) and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    print(f"[警告] 未找到前端 dist 目录: {frontend_dist}，请先在 ABUS 下执行 npm run build")


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
