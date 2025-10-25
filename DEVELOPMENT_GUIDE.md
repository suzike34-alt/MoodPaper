# MoodPaper 开发指南

## 🚀 快速开始

### 环境要求
- Node.js 18+
- Python 3.8+
- npm 或 yarn

### 安装步骤

#### 1. 后端设置
```bash
cd /Users/maimai/MoodPaper

# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量（复制.env.example并修改）
cp .env.example .env
# 编辑.env文件，添加API密钥

# 启动后端服务
python backend/main.py
```

#### 2. 前端设置
```bash
cd "/Users/maimai/MoodPaper/MoodPaper Web App Design"

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000

## 📂 关键文件说明

### 核心文件

#### `prompts.py` - Prompt生成核心
**作用**: 将用户心情转化为AI图像生成的Prompt

**关键函数**:
```python
def understand_mood(mood_text: str, selected_style: str) -> str
    """
    智能理解用户心情，转化为具体视觉场景

    示例:
    - "我像一只猫" → "a cute fluffy cat peacefully sleeping by the sunny window..."
    - "想变成星星" → "a beautiful twinkling star shining brightly in the vast night sky..."
    """

def build_wallpaper_prompt(mood_keyword: str, selected_style: str) -> Tuple[str, str]
    """
    生成完整Prompt

    Returns: (positive_prompt, negative_prompt)
    """
```

**如何扩展场景库**:
```python
# 在 MOOD_SCENE_PATTERNS 中添加新元素
MOOD_SCENE_PATTERNS = {
    "新元素": [
        "场景描述1, 氛围词, 情绪词",
        "场景描述2, 氛围词, 情绪词",
    ],
}
```

#### `App.tsx` - 前端主组件
**作用**: 整个应用的UI和交互逻辑

**关键区域**:
```typescript
// 1. 状态管理 (Line 39-47)
const [mood, setMood] = useState("");
const [style, setStyle] = useState("");
const [wallpapers, setWallpapers] = useState<WallpaperItem[]>([]);
const [quota, setQuota] = useState<QuotaStatus | null>(null);

// 2. API调用 (Line 168-209)
const handleGenerate = async () => {
  // 生成壁纸逻辑
};

// 3. UI渲染 (Line 353-980)
return (
  <div className="min-h-screen">
    {/* 输入区 */}
    {/* 图片库 */}
  </div>
);
```

## 🎨 常见开发任务

### 1. 添加新的壁纸风格

#### 步骤1: 后端 (prompts.py)
```python
# 在 STYLE_CONFIGS 中添加
STYLE_CONFIGS: Dict[str, StyleConfig] = {
    "新风格key": {
        "name": "🎨 新风格",
        "core_modifiers": [
            "核心修饰词1",
            "核心修饰词2",
        ],
        "art_style": [
            "艺术风格1",
            "艺术风格2",
        ],
        "quality_params": "high quality, beautiful details, masterpiece",
        "negative": "ugly, bad quality..."
    }
}
```

#### 步骤2: 前端 (App.tsx)
```typescript
// 在 getStyleName 函数中添加映射（如果需要）
const getStyleName = (styleKey: string) => {
  const styleMap: { [key: string]: string } = {
    "新风格key": "新风格中文名",
  };
  // ...
};
```

### 2. 修改UI样式

#### 配色
在 `App.tsx` 中搜索颜色类名:
- 主色: `from-pink-400`
- 卡片: `bg-white/95`
- 按钮: `from-pink-300 to-purple-300`

#### 间距
使用 Tailwind 的间距类:
- `p-{n}`: padding
- `m-{n}`: margin
- `gap-{n}`: flex/grid gap

#### 圆角
- 卡片: `rounded-3xl`
- 按钮: `rounded-2xl`
- 小元素: `rounded-xl`

### 3. 添加新的心情场景

在 `prompts.py` 的 `MOOD_SCENE_PATTERNS` 中添加:
```python
MOOD_SCENE_PATTERNS = {
    "新关键词": [
        "具体场景描述1, 氛围, 情绪",
        "具体场景描述2, 氛围, 情绪",
        # 可以添加多个变体
    ],
}
```

**注意**: 场景描述应该:
- ✅ 具体可视化（"猫在窗边睡觉" ✅）
- ❌ 避免抽象（"猫的感觉" ❌）
- ✅ 包含氛围和情绪词
- ✅ 使用英文（AI模型要求）

### 4. 修改Tooltip样式

#### CSS部分 (App.tsx Line 355-359)
```tsx
<style>{`
  .btn-tooltip:hover .tooltip-text {
    opacity: 1 !important;
  }
`}</style>
```

#### HTML结构
```tsx
<div className="relative btn-tooltip">
  <button>...</button>
  <div className="absolute ... opacity-0 tooltip-text ...">
    <div className="font-medium text-gray-800">提示文字</div>
    <div className="absolute ... border-b-white"></div> {/* 箭头 */}
  </div>
</div>
```

## 🐛 调试指南

### 前端调试

#### 1. 检查控制台
```typescript
// 添加日志
console.log("变量值:", someVariable);
console.error("错误信息:", error);
```

#### 2. 检查网络请求
1. 打开浏览器开发者工具
2. 切换到 Network 标签
3. 查看 API 请求和响应

#### 3. 检查状态
使用 React Developer Tools:
```bash
# Chrome扩展: React Developer Tools
# 查看组件状态和Props
```

### 后端调试

#### 1. 检查Prompt生成
```bash
# 运行测试
cd /Users/maimai/MoodPaper
python prompts.py

# 查看生成的Prompt
```

#### 2. 检查API响应
```bash
# 使用curl测试API
curl http://localhost:8000/api/styles

# 查看后端日志
# (查看运行python backend/main.py的终端)
```

## 🔧 常见问题解决

### 问题1: 下载按钮变成查看
**症状**: 点击下载打开新标签页
**检查**: `handleDownload` 函数是否使用了 Blob URL
**位置**: App.tsx Line 289-314

### 问题2: Tooltip不显示
**症状**: 悬停按钮时Tooltip不出现
**检查**:
1. 容器是否有 `btn-tooltip` 类
2. Tooltip元素是否有 `tooltip-text` 类
3. CSS是否包含 `.btn-tooltip:hover .tooltip-text`

### 问题3: 图片与心情不符
**症状**: 生成的图片内容与输入心情无关
**检查**:
1. `prompts.py` 的 `understand_mood` 函数是否正确匹配关键词
2. 心情场景库是否包含该关键词
3. 查看生成的Prompt（运行 `python prompts.py`）

### 问题4: API请求失败
**症状**: 前端提示"生成失败"或其他错误
**检查**:
1. 后端服务是否启动 (http://localhost:8000)
2. 浏览器控制台Network标签查看具体错误
3. 后端终端查看错误日志
4. 检查 `.env` 文件配置

## 📝 代码规范

### TypeScript/React

```typescript
// ✅ 好的写法
interface Props {
  title: string;
  count: number;
}

const MyComponent: React.FC<Props> = ({ title, count }) => {
  // 组件逻辑
  return <div>{title}</div>;
};

// ❌ 避免的写法
function MyComponent(props: any) {  // 不要用 any
  return <div>{props.title}</div>;
}
```

### Python

```python
# ✅ 好的写法
def process_mood(mood: str, style: str) -> Dict[str, Any]:
    """
    处理用户心情

    Args:
        mood: 用户输入的心情
        style: 壁纸风格

    Returns:
        处理结果字典
    """
    result = {"mood": mood}
    return result

# ❌ 避免的写法
def process_mood(mood, style):  # 缺少类型提示
    result = {"mood": mood}
    return result
```

## 🚀 性能优化

### 前端优化

1. **图片懒加载**（已实现）
```tsx
<img loading="lazy" src={image} alt={alt} />
```

2. **避免不必要的重渲染**
```typescript
// 使用 useMemo 缓存计算结果
const favoriteWallpapers = useMemo(
  () => wallpapers.filter(item => item.isFavorite),
  [wallpapers]
);
```

3. **API请求优化**
- 合并多个请求
- 使用防抖（debounce）

### 后端优化

1. **缓存Prompt**
2. **异步图片生成**
3. **CDN存储图片**

## 📦 部署流程

### 前端部署

```bash
cd "/Users/maimai/MoodPaper/MoodPaper Web App Design"

# 构建生产版本
npm run build

# build目录包含所有静态文件
# 可以部署到: Vercel, Netlify, GitHub Pages等
```

### 后端部署

```bash
cd /Users/maimai/MoodPaper

# 使用Gunicorn部署FastAPI
pip install gunicorn uvicorn[standard]

# 启动服务
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🔐 安全注意事项

1. **API密钥**: 永远不要提交 `.env` 到Git
2. **CORS配置**: 生产环境限制允许的来源
3. **输入验证**: 验证所有用户输入
4. **文件上传**: 限制文件大小和类型

## 📚 学习资源

- React: https://react.dev
- TypeScript: https://www.typescriptlang.org
- Tailwind CSS: https://tailwindcss.com
- FastAPI: https://fastapi.tiangolo.com
- Vite: https://vitejs.dev
