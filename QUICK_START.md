# 🚀 MoodPaper 快速启动指南

## ✅ 当前状态

**🎉 全部服务已启动并运行！**

| 服务 | 状态 | 地址 |
|------|------|------|
| **前端** | 🟢 运行中 | http://localhost:3000 |
| **后端** | 🟢 运行中 | http://localhost:8000 |
| **API 文档** | 🟢 可用 | http://localhost:8000/docs |

---

## 🎨 立即开始使用

### 1. 打开浏览器

```
http://localhost:3000
```

### 2. 生成你的第一张情绪壁纸

1. 输入你的心情（例如：开心、平静、治愈）
2. 选择壁纸风格（疗愈系、能量系、梦幻系等）
3. 点击"生成我的情绪壁纸"
4. 等待 30-60 秒
5. 查看生成的壁纸和签文

### 3. 升级超清（可选）

- 如果喜欢某张壁纸，点击"升级超清"按钮
- 等待 30-60 秒生成 2K 高清版本
- 下载标清或超清版本

---

## 📊 今日配额

- **标清生成**: 2/2 次
- **超清升级**: 1/1 次

配额每日自动重置（UTC 时间）

---

## 🛑 停止服务

```bash
# 停止后端
kill 15550

# 停止前端
kill 21175
```

---

## 🔄 重新启动

### 使用一键脚本
```bash
cd /Users/maimai/MoodPaper
./start.sh
```

### 手动启动

**终端1 - 后端**:
```bash
cd /Users/maimai/MoodPaper/backend
python3 main.py
```

**终端2 - 前端**:
```bash
cd "/Users/maimai/MoodPaper/MoodPaper Web App Design"
npm run dev
```

---

## 📚 更多信息

- **完整文档**: [README_FULLSTACK.md](README_FULLSTACK.md)
- **部署报告**: [DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md)
- **成本分析**: [COST_ESTIMATION.md](COST_ESTIMATION.md)
- **测试脚本**: `./test_api.sh`

---

## 💡 提示

- 第一次生成可能需要更长时间
- 确保网络连接正常
- 检查 .env 文件中的 API 密钥
- 查看日志：`/tmp/moodpaper_backend.log` 和 `/tmp/moodpaper_frontend.log`

---

**🎊 现在就开始创作你的情绪壁纸吧！**

打开浏览器访问: **http://localhost:3000**
