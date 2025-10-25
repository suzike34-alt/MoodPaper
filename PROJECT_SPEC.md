# MoodPaper 项目规范文档

## 📋 项目概述

**项目名称**: MoodPaper - AI 情绪壁纸生成器
**版本**: v2.0
**最后更新**: 2025-10-26

MoodPaper 是一个基于 AI 的情绪壁纸生成应用，将用户的心情转化为独特的壁纸艺术。

## 🏗️ 技术栈

### 前端
- **框架**: React 18.3.1 + TypeScript
- **构建工具**: Vite 6.3.5
- **UI组件**: Radix UI + Tailwind CSS
- **动画**: Motion (Framer Motion) 12.23.24
- **图片展示**: React Responsive Masonry
- **开发端口**: http://localhost:3000

### 后端
- **框架**: FastAPI (Python)
- **端口**: http://localhost:8000
- **图像生成**: AI API集成
- **数据存储**: JSON文件（history.json, quota.json）

## 📁 项目结构

```
MoodPaper/
├── backend/                    # 后端API服务
│   └── (FastAPI相关文件)
├── MoodPaper Web App Design/   # 前端React应用
│   ├── src/
│   │   ├── App.tsx            # 主应用组件
│   │   ├── main.tsx           # 应用入口
│   │   └── components/        # UI组件库
│   ├── package.json           # 前端依赖
│   └── vite.config.ts         # Vite配置
├── cache/                      # 缓存数据
│   ├── history.json           # 生成历史
│   └── quota.json             # 配额数据
├── output/                     # 生成的图片存储
├── prompts.py                 # Prompt生成核心逻辑
├── config.py                  # 配置文件
├── utils.py                   # 工具函数
└── PROJECT_SPEC.md            # 本文档
```

## 🎨 核心数据结构

### 1. WallpaperItem (前端)
```typescript
interface WallpaperItem {
  id: string;              // 唯一标识符
  image: string;           // 图片URL
  mood: string;            // 用户输入的心情
  style: string;           // 壁纸风格 (healing/energetic/dreamy/minimalist/natural)
  quote?: string;          // 治愈签文
  hd_path?: string;        // 超清图片路径
  isFavorite: boolean;     // 是否收藏
  aspect_ratio?: string;   // 宽高比 (1:1/9:16/16:9)
  original_path?: string;  // 原始图片路径
  timestamp?: string;      // 时间戳
}
```

### 2. QuotaStatus (前端)
```typescript
interface QuotaStatus {
  standard_generate: {
    used: number;
    limit: number;
    remaining: number;
  };
  hd_upgrade: {
    used: number;
    limit: number;
    remaining: number;
  };
  date: string;
}
```

### 3. StyleConfig (后端 prompts.py)
```python
class StyleConfig(TypedDict):
    name: str                     # 显示名称
    core_modifiers: List[str]     # 核心修饰词
    art_style: List[str]          # 艺术风格
    quality_params: str           # 画质参数
    negative: str                 # 负面提示
```

## 🎯 核心功能模块

### 1. Prompt 生成系统 (prompts.py)

**核心原则**: 心情优先，场景化表达

**主要函数**:
- `understand_mood(mood_text: str, selected_style: str) -> str`
  - 将用户心情转化为具体视觉场景
  - 智能理解表达方式（"我像一只猫"、"想变成星星"）

- `build_wallpaper_prompt(mood_keyword: str, selected_style: str) -> Tuple[str, str]`
  - 生成完整的图像生成prompt
  - 返回：(positive_prompt, negative_prompt)

**Prompt 结构权重**:
1. 核心心情场景 (70%) - 最重要！
2. 风格修饰词 (20%)
3. 艺术风格 (5%)
4. 画质参数 (5%)

**支持的壁纸风格**:
| key | 名称 | 特点 |
|-----|------|------|
| healing | 🌸 疗愈 | 水彩手绘、温馨治愈、柔和色彩 |
| energetic | ⚡ 能量 | 活力插画、鲜艳色彩、动态构图 |
| dreamy | 🌙 梦幻 | 奇幻插画、柔焦光晕、魔法氛围 |
| minimalist | 🎯 极简 | 简约艺术、留白、禅意美学 |
| natural | 🌿 自然 | 风光摄影、自然光、宁静氛围 |

**心情场景库**:
- 动物相关：猫、狗
- 自然元素：花、星、云、海、山、雨
- 日常场景：咖啡、书、窗
- 情绪状态：孤独、平静、快乐、梦幻

### 2. 前端核心功能 (App.tsx)

**主要组件**:
- 情绪输入区（带打字机动画placeholder）
- 风格选择器
- 尺寸选择器（1:1/9:16/16:9）
- 图片库（生成历史 + 我的收藏）

**核心函数**:
```typescript
// 生成壁纸
handleGenerate() -> Promise<void>

// 下载图片（使用Blob强制下载）
handleDownload(wallpaper: WallpaperItem, useHD: boolean) -> Promise<void>

// 升级到超清
handleUpgradeHD(wallpaper: WallpaperItem) -> Promise<void>

// 切换收藏
toggleFavorite(id: string) -> Promise<void>

// 删除记录
handleDelete(id: string) -> Promise<void>
```

**UI交互特性**:
- 卡片悬停显示操作按钮
- 按钮Tooltip（使用自定义CSS `.btn-tooltip:hover .tooltip-text`）
- 瀑布流布局（React Responsive Masonry）
- 玻璃拟态设计

## 🔌 API 接口规范

### Base URL
```
http://localhost:8000
```

### 端点列表

#### 1. 获取风格列表
```
GET /api/styles
Response: {
  styles: Array<{
    key: string;
    name: string;
    description: string;
  }>
}
```

#### 2. 获取配额状态
```
GET /api/quota
Response: {
  success: boolean;
  status: QuotaStatus;
}
```

#### 3. 获取生成历史
```
GET /api/history
Response: {
  success: boolean;
  history: Array<WallpaperItem>;
}
```

#### 4. 生成壁纸
```
POST /api/generate
Body: {
  mood: string;
  style: string;
  aspect_ratio: "1:1" | "9:16" | "16:9";
}
Response: {
  success: boolean;
  data?: {
    id: string;
    image_path: string;
    quote: string;
  };
  detail?: string;
}
```

#### 5. 升级到超清
```
POST /api/upgrade
Body: {
  image_path: string;
  record_id: string;
}
Response: {
  success: boolean;
  hd_path?: string;
  detail?: string;
}
```

#### 6. 切换收藏
```
POST /api/favorite/toggle
Body: {
  record_id: string;
}
Response: {
  success: boolean;
}
```

#### 7. 删除记录
```
DELETE /api/history/{record_id}
Response: {
  success: boolean;
}
```

#### 8. 获取图片
```
GET /api/image/{filename}
Response: Image file
```

## 🎨 UI/UX 设计规范

### 配色方案
- **主色**: 粉色渐变 `from-pink-400 via-purple-400 to-blue-400`
- **背景**: 柔和渐变 `from-pink-50/80 via-purple-50/60 to-blue-50/80`
- **卡片**: 玻璃拟态 `rgba(255, 255, 255, 0.95)`
- **按钮**: 粉紫渐变 `from-pink-300 to-purple-300`

### 间距标准
- 容器外边距: `px-4 py-8 md:py-12`
- 卡片内边距: `p-8 md:p-12`
- 按钮间距: `gap-2`
- 圆角: `rounded-3xl` (卡片), `rounded-2xl` (按钮)

### 动画时长
- 悬停过渡: `duration-300`
- Tooltip显示: `duration-200`
- 卡片缩放: `hover:scale-[1.01]`

### Tooltip样式
```tsx
<div className="relative btn-tooltip">
  <button>...</button>
  <div className="... opacity-0 tooltip-text ...">Tooltip内容</div>
</div>

// CSS
.btn-tooltip:hover .tooltip-text {
  opacity: 1 !important;
}
```

## 📝 开发规范

### 命名约定
- **组件**: PascalCase (e.g., `WallpaperCard`)
- **函数**: camelCase (e.g., `handleGenerate`)
- **常量**: UPPER_SNAKE_CASE (e.g., `API_BASE_URL`)
- **类型**: PascalCase (e.g., `WallpaperItem`)

### 代码组织
1. **Import顺序**: React相关 → UI组件 → 工具函数
2. **类型定义**: 文件顶部
3. **常量**: 类型定义之后
4. **函数**: 按照调用顺序排列
5. **JSX**: 文件末尾

### 错误处理
```typescript
try {
  // 操作
} catch (err) {
  console.error("操作失败:", err);
  alert("用户友好的错误提示");
}
```

## 🚀 部署检查清单

### 前端
- [ ] 运行 `npm run build`
- [ ] 检查构建产物在 `build/` 目录
- [ ] 测试所有功能（生成、下载、收藏、删除）
- [ ] 检查不同屏幕尺寸的响应式表现

### 后端
- [ ] 确保 `.env` 文件配置正确
- [ ] 检查 API 密钥有效性
- [ ] 测试所有 API 端点
- [ ] 检查配额管理正常工作
- [ ] 确保 `output/` 和 `cache/` 目录有写权限

## 🐛 已知问题和解决方案

### 1. 下载变成查看
**问题**: 点击下载按钮打开新标签页
**解决**: 使用 Blob URL 强制下载（已修复）

### 2. Tooltip不显示
**问题**: 嵌套 `group` 导致Tooltip失效
**解决**: 使用自定义CSS `.btn-tooltip` + `.tooltip-text`（已修复）

### 3. 图片与心情无关
**问题**: 技术参数掩盖心情表达
**解决**: 重构Prompt系统，心情场景优先（v2.0已解决）

## 📞 技术支持

- **文档**: 查看本文档和 `DEVELOPMENT_GUIDE.md`
- **问题**: 检查 console 日志
- **备份**: 重要修改前备份文件

## 📊 版本历史

### v2.0 (2025-10-26)
- ✅ 重构Prompt系统（心情中心化）
- ✅ 修复下载功能
- ✅ 修复收藏页面按钮显示
- ✅ 优化Tooltip系统
- ✅ 添加项目规范文档

### v1.0 (2025-10-24)
- ✅ 初始版本
- ✅ 基础UI和功能
