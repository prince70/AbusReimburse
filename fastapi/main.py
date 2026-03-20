from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, records, audit, finance, base

app = FastAPI(title="报销管理系统 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(records.router, prefix="/api/v1", tags=["报销单"])
app.include_router(audit.router, prefix="/api/v1", tags=["审批"])
app.include_router(finance.router, prefix="/api/v1", tags=["财务"])
app.include_router(base.router, prefix="/api/v1", tags=["基础数据"])


@app.get("/")
def root():
    return {"message": "报销管理系统 API 运行中", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
