# MoodPaper Backend API

FastAPI 后端服务，为 React 前端提供 RESTful API。

## 功能

- 🎨 壁纸生成（标清 1024x1024）
- ⭐ 超清升级（2048x2048）
- 📊 配额管理（每日限额）
- 📜 历史记录管理
- ❤️ 收藏功能
- 👤 会员管理

## 快速开始

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并填写 API 密钥：

```bash
cp .env.example .env
```

**注意**: API 密钥应该从父目录的 `.env` 文件继承。

### 3. 启动服务器

```bash
python main.py
```

或使用 uvicorn 命令：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 基础

- `GET /` - 服务信息
- `GET /health` - 健康检查
- `GET /api/styles` - 获取所有风格列表

### 配额管理

- `GET /api/quota` - 获取配额状态

### 壁纸生成

- `POST /api/generate` - 生成标清壁纸
  ```json
  {
    "mood": "开心",
    "style": "healing"
  }
  ```

- `POST /api/upgrade` - 升级到超清
  ```json
  {
    "image_path": "output/xxx.png",
    "record_id": "xxx-xxx-xxx"
  }
  ```

### 历史记录

- `GET /api/history` - 获取所有历史
- `GET /api/favorites` - 获取收藏列表
- `POST /api/favorite/toggle` - 切换收藏状态
  ```json
  {
    "record_id": "xxx-xxx-xxx"
  }
  ```
- `DELETE /api/history/{record_id}` - 删除记录

### 会员管理

- `GET /api/membership` - 获取会员状态
- `POST /api/membership/activate` - 激活会员
  ```json
  {
    "code": "VIPUSER2024"
  }
  ```

### 图片资源

- `GET /api/image/{filename}` - 查看图片
- `GET /api/download/{filename}?ratio=original` - 下载图片（支持裁剪）
  - ratio 参数: `original`, `16:9`, `9:16`

## CORS 配置

默认允许以下前端地址访问：

- http://localhost:5173 (Vite)
- http://localhost:3000 (Create React App)
- http://127.0.0.1:5173
- http://127.0.0.1:3000

## 目录结构

```
backend/
├── main.py              # FastAPI 主应用
├── requirements.txt     # Python 依赖
├── .env.example         # 环境变量示例
└── README.md           # 本文件
```

## 开发模式

启动时会自动启用热重载，修改代码后服务器会自动重启。

## 部署

### 使用 Gunicorn (生产环境)

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### 使用 Docker

```bash
# 构建镜像
docker build -t moodpaper-backend .

# 运行容器
docker run -p 8000:8000 moodpaper-backend
```

## 注意事项

1. 确保父目录的 `.env` 文件包含所有必需的 API 密钥
2. 确保 `output/` 目录存在且有写入权限
3. 确保 `cache/` 目录存在（用于配额、历史等数据）
4. 生产环境建议使用 Nginx 反向代理
5. 生产环境建议关闭 `reload` 模式

## 技术栈

- **FastAPI** - 现代高性能 Web 框架
- **Uvicorn** - ASGI 服务器
- **Pydantic** - 数据验证
- **Python 3.8+** - 运行环境
