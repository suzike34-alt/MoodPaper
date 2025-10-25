# 🎨 MoodPaper - AI 情绪壁纸生成器

> 输入你的心情，让 AI 为你创作专属的治愈壁纸和温暖签文

---

## 📖 项目简介

MoodPaper 是一个基于 AI 的情绪壁纸生成应用。用户只需输入当前的心情（如"焦虑"、"快乐"、"平静"），选择喜欢的壁纸风格，AI 就会自动生成：
- 🖼️ **4K 高清壁纸**（使用 Stable Diffusion AI 模型）
- 💬 **15 字内的疗愈签文**（使用 OpenAI GPT 模型）

---

## ✨ 核心功能

1. **心情输入**：自由输入任何心情关键词
2. **风格选择**：5 种壁纸风格可选
   - 🌸 疗愈（温暖柔和）
   - ⚡ 能量（活力动感）
   - 🌙 梦幻（唯美梦境）
   - 🎯 极简（简约禅意）
   - 🌿 自然（自然风光）
3. **AI 生成**：自动生成 4K 壁纸和签文
4. **一键下载**：下载高清壁纸到本地

---

## 🛠️ 技术栈

### 前端
- **框架**：React + Vite + TypeScript
- **UI 组件**：Radix UI + Tailwind CSS
- **状态管理**：React Hooks

### 后端
- **框架**：FastAPI (Python)
- **AI 图像生成**：Stability AI + Replicate (备选)
- **AI 文本生成**：OpenRouter (Claude 3.5 Sonnet)
- **图像处理**：Pillow
- **数据存储**：JSON 本地文件

### 核心特性
- 🧠 **智能情绪识别**：自动提取关键词和视觉元素
- 🎨 **模块化 Prompt**：8层结构确保高度多样性
- 💅 **年轻女性审美**：ins风、莫兰迪色、现代极简
- 📸 **专业摄影效果**：胶片质感、光影构图

---

## 📋 前置要求

在开始之前，请确保你的电脑已安装：
- **Python 3.8+**（推荐 3.10 或 3.11）
- **pip**（Python 包管理器）
- **VS Code**（或其他代码编辑器）

---

## 🚀 快速开始（新手向）

### 第一步：打开项目文件夹

1. 打开终端（Terminal）
2. 进入项目目录：
   ```bash
   cd /Users/maimai/MoodPaper
   ```

### 第二步：安装 Python 依赖包

在终端运行以下命令：
```bash
pip install -r requirements.txt
```

**解释**：这条命令会自动安装项目需要的所有 Python 库（Streamlit、Replicate、OpenAI 等）

**等待时间**：大约 1-3 分钟

### 第三步：获取 API 密钥

你需要注册两个服务并获取 API 密钥：

#### 3.1 获取 Replicate API Token（免费）
1. 访问：https://replicate.com
2. 点击右上角 **Sign Up** 注册账号（可以用 GitHub 登录）
3. 登录后，访问：https://replicate.com/account/api-tokens
4. 复制你的 API Token（格式类似：`r8_xxxxxxxxxxxx`）

#### 3.2 获取 OpenAI API Key（需付费）
1. 访问：https://platform.openai.com
2. 注册并登录账号
3. 访问：https://platform.openai.com/api-keys
4. 点击 **Create new secret key** 创建密钥
5. 复制你的 API Key（格式类似：`sk-xxxxxxxxxxxx`）

**注意**：OpenAI API 需要充值才能使用（建议充值 $5-10 美元）

### 第四步：配置 API 密钥

1. 在项目文件夹中，复制 `.env.example` 文件，重命名为 `.env`
   ```bash
   cp .env.example .env
   ```

2. 用 VS Code 打开 `.env` 文件：
   ```bash
   code .env
   ```

3. 将文件内容修改为（替换为你的真实密钥）：
   ```
   REPLICATE_API_TOKEN=你的_Replicate_Token
   OPENAI_API_KEY=你的_OpenAI_Key
   ```

4. 保存文件（Command + S 或 Ctrl + S）

### 第五步：运行应用

在终端运行：
```bash
streamlit run app.py
```

**成功标志**：你会看到类似这样的输出：
```
You can now view your Streamlit app in your browser.

Local URL: http://localhost:8501
Network URL: http://192.168.x.x:8501
```

浏览器会自动打开，如果没有自动打开，手动访问：http://localhost:8501

---

## 🎯 使用教程

1. 在输入框中输入你的心情（例如：焦虑、快乐、平静）
2. 在下拉菜单中选择壁纸风格（疗愈、能量、梦幻、极简、自然）
3. 点击 **"✨ 生成我的专属壁纸"** 按钮
4. 等待 30-60 秒（AI 生成需要时间）
5. 查看生成的壁纸和签文
6. 点击 **"📥 下载壁纸 (4K)"** 保存到本地

---

## 📁 项目结构

```
MoodPaper/
├── app.py              # 主程序文件（核心代码）
├── requirements.txt    # Python 依赖包列表
├── .env.example        # API 密钥配置模板
├── .env                # API 密钥配置（你需要创建，包含敏感信息）
├── .gitignore          # Git 忽略文件配置
└── README.md           # 项目说明文档（本文件）
```

---

## 🔧 常见问题解决

### 问题 1：提示"请先配置 API 密钥"
**原因**：`.env` 文件不存在或配置错误

**解决方法**：
1. 检查项目文件夹中是否有 `.env` 文件（不是 `.env.example`）
2. 打开 `.env` 文件，确认密钥已正确填写
3. 重启应用（在终端按 `Ctrl + C` 停止，然后重新运行 `streamlit run app.py`）

### 问题 2：运行 `pip install` 报错
**原因**：Python 环境问题

**解决方法**：
```bash
# 使用 pip3 代替 pip
pip3 install -r requirements.txt

# 或者使用 python -m pip
python -m pip install -r requirements.txt
```

### 问题 3：图片生成失败
**原因**：Replicate API Token 无效或余额不足

**解决方法**：
1. 检查 Replicate API Token 是否正确复制
2. 登录 Replicate 网站检查账户状态
3. 查看错误信息（应用会显示具体错误）

### 问题 4：签文生成失败
**原因**：OpenAI API Key 无效或余额不足

**解决方法**：
1. 检查 OpenAI API Key 是否正确复制
2. 登录 OpenAI 网站检查账户余额
3. 确认账户已完成充值

### 问题 5：生成速度很慢
**原因**：生成 4K 图片需要较长时间

**这是正常现象**：
- Stable Diffusion 生成 4K 图片通常需要 30-60 秒
- 请耐心等待，不要重复点击按钮

---

## 💰 成本估算

- **Replicate**：新用户有免费额度，之后按使用量计费（生成一张 4K 图片约 $0.02-0.05）
- **OpenAI**：GPT-3.5-turbo 生成签文约 $0.0001-0.0003/次

**预估**：生成 100 张壁纸+签文，总成本约 $2-5 美元

---

## 📝 代码学习指南

作为新手，建议你按以下顺序阅读代码：

1. **先看 `app.py` 的注释**：每一行代码都有详细的中文解释
2. **从 `main()` 函数开始**：这是程序的入口
3. **理解数据流**：输入心情 → 调用 API → 显示结果
4. **尝试修改**：改变风格提示词、调整界面文字等

**学习建议**：
- 不懂的地方可以问我
- 尝试修改代码，看看会发生什么
- 出错不要怕，错误信息会告诉你问题在哪

---

## 🎓 进阶功能建议

当你熟悉基础功能后，可以尝试添加：
- [ ] 更多壁纸风格（科技感、复古、水彩等）
- [ ] 历史记录功能（保存之前生成的壁纸）
- [ ] 自定义分辨率（支持手机壁纸、iPad 壁纸等）
- [ ] 批量生成（一次生成多张壁纸）
- [ ] 用户登录系统
- [ ] 分享到社交媒体

---

## 📞 需要帮助？

如果你遇到任何问题，可以：
1. 查看本文档的"常见问题解决"部分
2. 检查 `app.py` 中的注释
3. 随时问我（Claude）任何问题

---

## 📜 开源协议

本项目仅供学习和个人使用。

---

## 🎉 恭喜你！

你已经完成了第一个 AI 项目的搭建！

现在开始享受创作的乐趣吧~ 🚀
