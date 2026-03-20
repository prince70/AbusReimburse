# 报销管理系统 (Bxxt)

企业报销管理系统，支持员工提交报销单、经理审批、财务审批的双审批流程。

## 技术栈

| 端 | 技术 |
|---|---|
| 前端 | Vue 3 + TypeScript + Element Plus + Vite + Pinia |
| 后端 | Python FastAPI + pyodbc |
| 数据库 | SQL Server |

## 目录结构

```
Bxxt/
├── ABUS/                # 前端项目
│   ├── src/
│   │   ├── api/         # axios 封装 + 接口函数
│   │   ├── components/  # 公共组件 (Layout)
│   │   ├── router/      # Vue Router
│   │   ├── stores/      # Pinia 状态管理
│   │   └── views/       # 页面组件
│   ├── index.html
│   ├── package.json
│   └── vite.config.ts
├── fastapi/             # 后端项目
│   ├── routers/
│   │   ├── auth.py      # 认证接口
│   │   ├── records.py   # 报销单 CRUD
│   │   ├── audit.py     # 经理审批
│   │   ├── finance.py   # 财务审批
│   │   └── base.py      # 基础数据 + 统计
│   ├── database.py      # 数据库连接
│   ├── main.py          # FastAPI 入口
│   └── requirements.txt
└── init_db.sql          # 数据库初始化脚本
```

## 快速启动

### 1. 初始化数据库

在 SQL Server (192.168.10.202) 上执行 `init_db.sql`。

### 2. 启动后端

```bash
cd fastapi
pip install -r requirements.txt
python main.py
# 服务运行在 http://0.0.0.0:8002
```

### 3. 启动前端（开发）

```bash
cd ABUS
npm install
npm run dev
# 访问 http://localhost:5173
```

### 4. 前端生产构建

```bash
cd ABUS
npm run build
# dist/ 目录即为静态文件，部署到 Web 服务器即可
```

## 默认账户

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 系统管理员 |
| finance | finance123 | 财务管理员 |

> 注册新员工后，需由系统管理员在数据库中将其角色改为「经理」才可进行审批操作。

## 业务流程

```
员工提交报销单 (status=待审)
      ↓
经理审批通过 → status=已批, finance_status=待审（自动分配财务）
经理退回   → status=退回
      ↓
财务审批通过 → finance_status=已批（流程完成）
财务退回   → finance_status=退回
```

## API 文档

启动后端后访问：http://192.168.10.202:8002/docs
