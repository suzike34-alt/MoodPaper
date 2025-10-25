import { useState, useEffect } from "react";
import { Input } from "./components/ui/input";
import { Button } from "./components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Heart, Sparkles, Loader2, Image, Smartphone, Monitor, Download, Trash2, Zap } from "lucide-react";
import Masonry, { ResponsiveMasonry } from "react-responsive-masonry";
import { motion } from "motion/react";

// Backend API URL
const API_BASE_URL = "http://localhost:8000";

interface WallpaperItem {
  id: string;
  image: string;
  mood: string;
  style: string;
  quote?: string;
  hd_path?: string;
  isFavorite: boolean;
  aspect_ratio?: string;
  original_path?: string;
  timestamp?: string;
}

interface QuotaStatus {
  standard_generate: { used: number; limit: number; remaining: number };
  hd_upgrade: { used: number; limit: number; remaining: number };
  date: string;
}

interface StyleOption {
  key: string;
  name: string;
  description: string;
}

export default function App() {
  const [mood, setMood] = useState("");
  const [style, setStyle] = useState("");
  const [aspectRatio, setAspectRatio] = useState<"1:1" | "9:16" | "16:9">("9:16");
  const [isGenerating, setIsGenerating] = useState(false);
  const [wallpapers, setWallpapers] = useState<WallpaperItem[]>([]);
  const [quota, setQuota] = useState<QuotaStatus | null>(null);
  const [styles, setStyles] = useState<StyleOption[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [placeholderText, setPlaceholderText] = useState("");

  // 漂浮气泡的心情话语
  const moodBubbles = [
    { text: "想变成一只猫 🐱", x: "8%", y: "12%", delay: 0, rotate: -5 },
    { text: "不想洗澡 🛁", x: "78%", y: "18%", delay: 2, rotate: 3 },
    { text: "这朵花真好看 🌸", x: "12%", y: "68%", delay: 1, rotate: -3 },
    { text: "想吃草莓蛋糕 🍰", x: "82%", y: "72%", delay: 3, rotate: 5 },
    { text: "今天的云好软 ☁️", x: "3%", y: "38%", delay: 1.5, rotate: -4 },
    { text: "想变成一颗星星 ⭐", x: "88%", y: "42%", delay: 2.5, rotate: 2 },
  ];

  // Placeholder 示例文本
  const placeholderExamples = [
    "想变成一只猫",
    "不想洗澡",
    "这朵花真好看",
    "想吃草莓蛋糕",
    "今天的云好软",
    "想变成一颗星星"
  ];

  // 打字机动画效果
  useEffect(() => {
    let currentTextIndex = 0;
    let currentCharIndex = 0;
    let isDeleting = false;
    let timeoutId: NodeJS.Timeout;

    const type = () => {
      const currentText = placeholderExamples[currentTextIndex];

      if (isDeleting) {
        // 删除字符
        setPlaceholderText(currentText.substring(0, currentCharIndex - 1));
        currentCharIndex--;

        if (currentCharIndex === 0) {
          isDeleting = false;
          currentTextIndex = (currentTextIndex + 1) % placeholderExamples.length;
          timeoutId = setTimeout(type, 500); // 删除完后等待 500ms
        } else {
          timeoutId = setTimeout(type, 50); // 删除速度
        }
      } else {
        // 添加字符
        setPlaceholderText(currentText.substring(0, currentCharIndex + 1));
        currentCharIndex++;

        if (currentCharIndex === currentText.length) {
          isDeleting = true;
          timeoutId = setTimeout(type, 2000); // 显示完整文字后等待 2s
        } else {
          timeoutId = setTimeout(type, 150); // 打字速度
        }
      }
    };

    timeoutId = setTimeout(type, 500);

    return () => {
      clearTimeout(timeoutId);
    };
  }, []);

  // 获取配额状态
  const fetchQuota = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/quota`);
      const data = await response.json();
      if (data.success) {
        setQuota(data.status);
      }
    } catch (err) {
      console.error("获取配额失败:", err);
    }
  };

  // 获取历史记录
  const fetchHistory = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/history`);
      const data = await response.json();
      if (data.success) {
        const formattedHistory = data.history.map((item: any) => ({
          id: item.id,
          image: `${API_BASE_URL}/api/image/${item.original_path?.split("/").pop() || ""}`,
          mood: item.mood,
          style: item.style,
          quote: item.quote,
          hd_path: item.hd_path,
          isFavorite: item.is_favorite || false,
          aspect_ratio: item.aspect_ratio || "1:1",
          original_path: item.original_path,
          timestamp: item.timestamp,
        }));
        setWallpapers(formattedHistory);
      }
    } catch (err) {
      console.error("获取历史失败:", err);
    }
  };

  // 获取风格列表
  const fetchStyles = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/styles`);
      const data = await response.json();
      setStyles(data.styles || []);
    } catch (err) {
      console.error("获取风格列表失败:", err);
    }
  };

  // 初始化加载数据
  useEffect(() => {
    fetchQuota();
    fetchHistory();
    fetchStyles();
  }, []);

  // 生成壁纸
  const handleGenerate = async () => {
    if (!mood || !style) return;

    setIsGenerating(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          mood,
          style,
          aspect_ratio: aspectRatio,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "生成失败");
      }

      if (data.success) {
        // 刷新历史记录和配额
        await fetchHistory();
        await fetchQuota();

        // 清空输入
        setMood("");
        setStyle("");
      }
    } catch (err: any) {
      setError(err.message || "生成失败，请稍后重试");
      console.error("生成失败:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  // 升级到超清
  const handleUpgradeHD = async (wallpaper: WallpaperItem) => {
    if (wallpaper.hd_path) {
      alert("该壁纸已经是超清版本");
      return;
    }

    try {
      const filename = wallpaper.original_path?.split("/").pop() || wallpaper.image.split("/").pop();

      const response = await fetch(`${API_BASE_URL}/api/upgrade`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image_path: filename,
          record_id: wallpaper.id,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "升级失败");
      }

      if (data.success) {
        alert("超清壁纸生成成功！");
        await fetchHistory();
        await fetchQuota();
      }
    } catch (err: any) {
      alert(err.message || "升级失败，请稍后重试");
      console.error("升级失败:", err);
    }
  };

  // 切换收藏状态
  const toggleFavorite = async (id: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/favorite/toggle`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ record_id: id }),
      });

      const data = await response.json();

      if (data.success) {
        await fetchHistory();
      }
    } catch (err) {
      console.error("切换收藏失败:", err);
    }
  };

  // 删除记录
  const handleDelete = async (id: string) => {
    if (!confirm("确定要删除这条记录吗？")) return;

    try {
      const response = await fetch(`${API_BASE_URL}/api/history/${id}`, {
        method: "DELETE",
      });

      const data = await response.json();

      if (data.success) {
        await fetchHistory();
      }
    } catch (err) {
      console.error("删除失败:", err);
    }
  };

  // 下载图片
  const handleDownload = async (wallpaper: WallpaperItem, useHD: boolean = false) => {
    try {
      const filename = useHD && wallpaper.hd_path
        ? wallpaper.hd_path.split("/").pop()
        : wallpaper.original_path?.split("/").pop() || wallpaper.image.split("/").pop();

      // 使用 fetch 获取图片，然后创建 blob URL 强制下载
      const response = await fetch(`${API_BASE_URL}/api/image/${filename}`);
      const blob = await response.blob();
      const blobUrl = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = filename || "wallpaper.png";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // 清理 blob URL
      URL.revokeObjectURL(blobUrl);
    } catch (err) {
      console.error("下载失败:", err);
      alert("下载失败，请稍后重试");
    }
  };

  // 获取显示用的宽高比
  const getDisplayRatio = (originalRatio: string = "1:1") => {
    if (originalRatio === "9:16") return "3 / 4";
    if (originalRatio === "16:9") return "4 / 3";
    return "1 / 1";
  };

  // 获取分辨率文本
  const getResolutionText = (ratio: string) => {
    if (ratio === "1:1") return "1024×1024";
    if (ratio === "9:16") return "720×1280";
    if (ratio === "16:9") return "1280×720";
    return "";
  };

  // 获取比例名称
  const getRatioName = (ratio: string) => {
    if (ratio === "1:1") return "1:1 正方形";
    if (ratio === "9:16") return "9:16 手机";
    if (ratio === "16:9") return "16:9 电脑";
    return "";
  };

  // 获取风格中文名称
  const getStyleName = (styleKey: string) => {
    const styleMap: { [key: string]: string } = {
      "abstract": "抽象渐变",
      "nature": "自然风光",
      "minimal": "极简主义",
      "fantasy": "梦幻插画",
      "soft": "柔和色彩",
      "geometric": "几何图形",
      "natural": "自然风光",
      "cute": "可爱治愈",
      "warm": "温暖色调",
      "healing": "治愈系",
    };
    // 如果从 API 获取到了 styles，优先使用 API 的名称
    const apiStyle = styles.find(s => s.key === styleKey);
    if (apiStyle) return apiStyle.name;
    // 否则使用本地映射
    return styleMap[styleKey] || styleKey;
  };

  const favoriteWallpapers = wallpapers.filter((item) => item.isFavorite);

  return (
    <div className="min-h-screen relative overflow-x-hidden">
      <style>{`
        .btn-tooltip:hover .tooltip-text {
          opacity: 1 !important;
        }
      `}</style>
      {/* 渐变背景 - 柔和粉紫蓝渐变 */}
      <div className="fixed inset-0 bg-gradient-to-br from-pink-50/80 via-purple-50/60 to-blue-50/80" />

      {/* 中心柔光光晕 */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white/60 via-transparent to-transparent" />

      {/* 顶部光晕 */}
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-pink-100/30 via-transparent to-transparent" />

      {/* 噪点纹理 */}
      <div
        className="fixed inset-0 opacity-[0.015]"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' /%3E%3C/svg%3E")`,
        }}
      />

      {/* 漂浮气泡 */}
      {moodBubbles.map((bubble, index) => (
        <motion.div
          key={index}
          className="fixed pointer-events-none hidden lg:block z-[5]"
          style={{
            left: bubble.x,
            top: bubble.y,
          }}
          initial={{ opacity: 0, scale: 0.5, y: 30, rotate: 0 }}
          animate={{
            opacity: [0.85, 1, 0.85],
            scale: [0.98, 1.02, 0.98],
            y: [0, -15, 0],
            rotate: [bubble.rotate - 2, bubble.rotate + 2, bubble.rotate - 2],
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            delay: bubble.delay,
            ease: "easeInOut",
          }}
        >
          <div
            className="px-6 py-3.5 rounded-full backdrop-blur-xl border-2 border-white/60 whitespace-nowrap shadow-2xl"
            style={{
              background: "linear-gradient(135deg, rgba(251, 194, 235, 0.85), rgba(206, 176, 252, 0.85))",
              boxShadow: "0 8px 32px rgba(251, 194, 235, 0.5), 0 4px 16px rgba(206, 176, 252, 0.4), inset 0 2px 4px rgba(255, 255, 255, 0.9)",
            }}
          >
            <p className="text-base text-white" style={{ fontWeight: 500, textShadow: "0 1px 2px rgba(0, 0, 0, 0.1)" }}>
              {bubble.text}
            </p>
          </div>
        </motion.div>
      ))}

      {/* 内容容器 */}
      <div className="relative z-10 container mx-auto px-4 py-8 md:py-12 max-w-7xl">
        {/* 顶部标题区 */}
        <header className="text-center mb-12">
          <div className="inline-flex items-center gap-3 mb-4">
            <Sparkles className="w-8 h-8 md:w-10 md:h-10 text-pink-400 drop-shadow-lg" />
            <h1
              className="text-4xl md:text-6xl bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 bg-clip-text text-transparent"
              style={{ fontWeight: 600 }}
            >
              MoodPaper
            </h1>
          </div>
          <p className="text-gray-600/80 mb-2" style={{ fontWeight: 500 }}>
            AI 情绪壁纸生成器 / AI Mood Wallpaper Generator
          </p>
          <p className="text-sm text-gray-500/70 max-w-2xl mx-auto">
            通过AI技术，将你的情绪转化为独特的壁纸艺术。每一张图片都是你心情的视觉诗篇。
          </p>
        </header>

        {/* 中间功能区 - 玻璃拟态卡片 */}
        <div className="max-w-3xl mx-auto mb-16">
          <div
            className="rounded-[2.5rem] p-8 md:p-12 backdrop-blur-2xl"
            style={{
              background: "linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85))",
              boxShadow: "0 10px 30px rgba(251, 194, 235, 0.25), 0 4px 12px rgba(209, 217, 230, 0.3), inset 0 1px 2px rgba(255, 255, 255, 1)",
            }}
          >
            <div className="space-y-6">
              {/* 情绪输入框 - 对话气泡样式 */}
              <div>
                <label className="flex items-center gap-3 mb-4 pl-2">
                  <Sparkles className="w-7 h-7 text-pink-400 animate-pulse" />
                  <span
                    className="text-[36px] text-pink-500"
                    style={{
                      fontWeight: 700,
                      textShadow: '0 2px 8px rgba(236, 72, 153, 0.4), 0 0 20px rgba(251, 194, 235, 0.6)'
                    }}
                  >
                    你现在的心情是？
                  </span>
                </label>
                <div className="relative btn-tooltip">
                  {/* 对话气泡尾巴 */}
                  <div
                    className="absolute -top-3 left-8 w-0 h-0"
                    style={{
                      borderLeft: "12px solid transparent",
                      borderRight: "12px solid transparent",
                      borderBottom: "12px solid rgba(251, 194, 235, 0.3)",
                    }}
                  />
                  <div
                    className="rounded-3xl overflow-hidden backdrop-blur-xl border-2 border-pink-200/60"
                    style={{
                      background: "linear-gradient(135deg, rgba(251, 194, 235, 0.25), rgba(255, 255, 255, 0.5))",
                      boxShadow: "0 8px 24px rgba(251, 194, 235, 0.3), inset 0 1px 2px rgba(255, 255, 255, 0.9)",
                    }}
                  >
                    <Input
                      value={mood}
                      onChange={(e) => setMood(e.target.value)}
                      placeholder={placeholderText}
                      className="border-0 bg-transparent px-6 py-6 focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-gray-400/70 text-gray-700"
                    />
                  </div>
                </div>
              </div>

              {/* 风格选择与尺寸选择 */}
              <div className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-4 items-end">
                {/* 风格选择 */}
                <div>
                  <label className="block mb-3 text-gray-700/80">
                    选择壁纸风格
                  </label>
                  <div
                    className="rounded-2xl overflow-hidden backdrop-blur-md border border-white/50"
                    style={{
                      background: "rgba(255, 255, 255, 0.4)",
                      boxShadow: "inset 0 2px 4px rgba(209, 217, 230, 0.3), inset 0 -1px 2px rgba(255, 255, 255, 0.8), 0 1px 2px rgba(255, 255, 255, 0.8)",
                    }}
                  >
                    <Select value={style} onValueChange={setStyle}>
                      <SelectTrigger className="border-0 bg-transparent px-6 py-6 focus:ring-0 focus:ring-offset-0">
                        <SelectValue placeholder="请选择风格" />
                      </SelectTrigger>
                      <SelectContent>
                        {styles.length > 0 ? (
                          styles.map((styleOption) => (
                            <SelectItem key={styleOption.key} value={styleOption.key}>
                              {styleOption.name}
                            </SelectItem>
                          ))
                        ) : (
                          <>
                            <SelectItem value="abstract">抽象渐变</SelectItem>
                            <SelectItem value="nature">自然风光</SelectItem>
                            <SelectItem value="minimal">极简主义</SelectItem>
                            <SelectItem value="fantasy">梦幻插画</SelectItem>
                            <SelectItem value="soft">柔和色彩</SelectItem>
                            <SelectItem value="geometric">几何图形</SelectItem>
                          </>
                        )}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* 图片尺寸选择 */}
                <div>
                  <label className="block mb-3 text-gray-700/80 text-sm">
                    尺寸
                  </label>
                  <div className="flex gap-2">
                    {/* 1:1 正方形 */}
                    <div className="relative group">
                      <button
                        onClick={() => setAspectRatio("1:1")}
                        className={`p-3 rounded-xl backdrop-blur-md border transition-all duration-200 hover:scale-110 ${
                          aspectRatio === "1:1"
                            ? "border-pink-300 bg-gradient-to-br from-pink-100/60 to-purple-100/40 shadow-md"
                            : "border-white/50 bg-white/30 hover:bg-white/40"
                        }`}
                      >
                        <Image className={`w-5 h-5 ${aspectRatio === "1:1" ? "text-pink-500" : "text-gray-500"}`} />
                      </button>
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-4 py-2.5 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                        <div className="font-semibold text-gray-800">1:1 正方形</div>
                        <div className="text-[11px] text-gray-600 mt-0.5">1024×1024</div>
                        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px border-[6px] border-transparent border-t-white"></div>
                      </div>
                    </div>

                    {/* 9:16 手机 */}
                    <div className="relative group">
                      <button
                        onClick={() => setAspectRatio("9:16")}
                        className={`p-3 rounded-xl backdrop-blur-md border transition-all duration-200 hover:scale-110 ${
                          aspectRatio === "9:16"
                            ? "border-pink-300 bg-gradient-to-br from-pink-100/60 to-purple-100/40 shadow-md"
                            : "border-white/50 bg-white/30 hover:bg-white/40"
                        }`}
                      >
                        <Smartphone className={`w-5 h-5 ${aspectRatio === "9:16" ? "text-pink-500" : "text-gray-500"}`} />
                      </button>
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-4 py-2.5 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                        <div className="font-semibold text-gray-800">9:16 手机</div>
                        <div className="text-[11px] text-gray-600 mt-0.5">720×1280</div>
                        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px border-[6px] border-transparent border-t-white"></div>
                      </div>
                    </div>

                    {/* 16:9 电脑 */}
                    <div className="relative group">
                      <button
                        onClick={() => setAspectRatio("16:9")}
                        className={`p-3 rounded-xl backdrop-blur-md border transition-all duration-200 hover:scale-110 ${
                          aspectRatio === "16:9"
                            ? "border-pink-300 bg-gradient-to-br from-pink-100/60 to-purple-100/40 shadow-md"
                            : "border-white/50 bg-white/30 hover:bg-white/40"
                        }`}
                      >
                        <Monitor className={`w-5 h-5 ${aspectRatio === "16:9" ? "text-pink-500" : "text-gray-500"}`} />
                      </button>
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-4 py-2.5 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                        <div className="font-semibold text-gray-800">16:9 电脑</div>
                        <div className="text-[11px] text-gray-600 mt-0.5">1280×720</div>
                        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-px border-[6px] border-transparent border-t-white"></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* 生成按钮 */}
              <Button
                onClick={handleGenerate}
                disabled={isGenerating || !mood || !style}
                className="w-full py-7 rounded-2xl relative overflow-hidden transition-all duration-300 hover:scale-[1.01] active:scale-[0.99] border border-white/40 text-white disabled:opacity-60"
                style={{
                  background: isGenerating
                    ? "linear-gradient(135deg, rgba(251, 194, 235, 0.8) 0%, rgba(166, 193, 238, 0.8) 100%)"
                    : "linear-gradient(135deg, rgb(251, 194, 235) 0%, rgb(166, 193, 238) 100%)",
                  boxShadow: isGenerating
                    ? "inset 0 2px 8px rgba(209, 217, 230, 0.5), inset 0 -1px 2px rgba(255, 255, 255, 0.3)"
                    : "0 4px 16px rgba(251, 194, 235, 0.4), 0 2px 8px rgba(166, 193, 238, 0.3), inset 0 1px 1px rgba(255, 255, 255, 0.5), inset 0 -1px 1px rgba(209, 217, 230, 0.2)",
                }}
              >
                <span className="relative z-10">
                  {isGenerating ? (
                    <>
                      <Loader2 className="mr-2 h-5 w-5 animate-spin inline" />
                      生成中...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-5 w-5 inline" />
                      生成我的情绪壁纸
                    </>
                  )}
                </span>
                {/* 柔光高光 */}
                <div
                  className="absolute inset-x-0 top-0 h-1/2 opacity-40"
                  style={{
                    background: "linear-gradient(to bottom, rgba(255, 255, 255, 0.6), transparent)",
                    borderRadius: "1rem 1rem 0 0",
                  }}
                />
              </Button>

              {/* 状态提示和配额显示 */}
              <div className="space-y-2.5 text-center">
                <p className="text-sm text-gray-500/70">
                  💡 生成壁纸需要 30-60 秒，请耐心等待
                </p>
                {quota && (
                  <div className="text-sm text-gray-500/70">
                    📷 标清生成: {quota.standard_generate.remaining}/{quota.standard_generate.limit} ⭐ 超清升级: {quota.hd_upgrade.remaining}/{quota.hd_upgrade.limit}
                  </div>
                )}
              </div>

              {/* 错误提示 */}
              {error && (
                <div className="p-4 rounded-2xl bg-red-50/80 border border-red-200/50 text-red-600 text-sm text-center">
                  {error}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 我的图片库 */}
        <div className="max-w-6xl mx-auto">
          <h2
            className="mb-3 text-center text-[36px] bg-gradient-to-r from-pink-400 via-purple-400 to-blue-400 bg-clip-text text-transparent"
            style={{ fontWeight: 600 }}
          >
            我的图片库
          </h2>

          <Tabs defaultValue="history" className="w-full">
            {/* 选项卡 */}
            <div className="flex justify-center mb-8">
              <TabsList
                className="rounded-full p-1.5 backdrop-blur-2xl border border-white/40"
                style={{
                  background: "linear-gradient(135deg, rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.5))",
                  boxShadow: "0 4px 16px rgba(209, 217, 230, 0.15), 0 1px 4px rgba(255, 255, 255, 0.8), inset 0 1px 1px rgba(255, 255, 255, 0.9)",
                }}
              >
                <TabsTrigger
                  value="history"
                  className="rounded-full px-8 py-3 data-[state=active]:bg-gradient-to-r data-[state=active]:from-pink-300/90 data-[state=active]:to-purple-300/90 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
                >
                  生成历史
                </TabsTrigger>
                <TabsTrigger
                  value="favorites"
                  className="rounded-full px-8 py-3 data-[state=active]:bg-gradient-to-r data-[state=active]:from-pink-300/90 data-[state=active]:to-purple-300/90 data-[state=active]:text-white data-[state=active]:shadow-lg transition-all duration-300"
                >
                  我的收藏
                </TabsTrigger>
              </TabsList>
            </div>

            {/* 生成历史 */}
            <TabsContent value="history" className="mt-0">
              {wallpapers.length === 0 ? (
                <div className="text-center py-20">
                  <Sparkles className="w-16 h-16 text-gray-300/60 mx-auto mb-4" />
                  <p className="text-gray-400/70">还没有生成过壁纸</p>
                  <p className="text-sm text-gray-300/60 mt-2">输入你的心情开始创作吧</p>
                </div>
              ) : (
                <ResponsiveMasonry columnsCountBreakPoints={{ 350: 1, 750: 2, 900: 3 }}>
                  <Masonry gutter="1.5rem">
                    {wallpapers.map((item) => (
                      <div
                        key={item.id}
                        className="group relative rounded-3xl overflow-hidden transition-all duration-300 hover:scale-[1.01] hover:shadow-2xl backdrop-blur-xl"
                        style={{
                          background: "linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85))",
                          boxShadow: "0 10px 30px rgba(251, 194, 235, 0.25), 0 4px 12px rgba(209, 217, 230, 0.3), inset 0 1px 2px rgba(255, 255, 255, 1)",
                        }}
                      >
                        {/* 图片 */}
                        <div className="relative overflow-hidden">
                          <img
                            src={item.image}
                            alt={item.mood}
                            className="w-full h-auto object-cover"
                            style={{ aspectRatio: getDisplayRatio(item.aspect_ratio) }}
                          />
                          {/* 操作按钮悬浮层 */}
                          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                            <div className="absolute top-4 right-4 flex gap-2">
                              {/* 下载按钮 */}
                              <div className="relative btn-tooltip">
                                <button
                                  onClick={() => handleDownload(item, false)}
                                  className="p-3 rounded-full backdrop-blur-2xl transition-all duration-300 hover:scale-110 border border-white/50"
                                  style={{
                                    background: "rgba(255, 255, 255, 0.85)",
                                    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9)",
                                  }}
                                >
                                  <Download className="w-5 h-5 text-gray-400" />
                                </button>
                                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-2 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                                  <div className="font-medium text-gray-800">下载</div>
                                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-[-1px] border-[6px] border-transparent border-b-white"></div>
                                </div>
                              </div>

                              {/* 超清升级/下载超清按钮 */}
                              {!item.hd_path ? (
                                <div className="relative btn-tooltip">
                                  <button
                                    onClick={() => handleUpgradeHD(item)}
                                    className="p-3 rounded-full backdrop-blur-2xl transition-all duration-300 hover:scale-110 border border-white/50"
                                    style={{
                                      background: "rgba(255, 255, 255, 0.85)",
                                      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9)",
                                    }}
                                  >
                                    <Zap className="w-5 h-5 text-pink-400" />
                                  </button>
                                  <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-2 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                                    <div className="font-medium text-gray-800">超清升级</div>
                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-[-1px] border-[6px] border-transparent border-b-white"></div>
                                  </div>
                                </div>
                              ) : (
                                <div className="relative btn-tooltip">
                                  <button
                                    onClick={() => handleDownload(item, true)}
                                    className="p-3 rounded-full backdrop-blur-2xl transition-all duration-300 hover:scale-110 border border-white/50"
                                    style={{
                                      background: "rgba(255, 255, 255, 0.85)",
                                      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9)",
                                    }}
                                  >
                                    <Download className="w-5 h-5 text-pink-400" />
                                  </button>
                                  <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-2 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                                    <div className="font-medium text-gray-800">下载超清</div>
                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-[-1px] border-[6px] border-transparent border-b-white"></div>
                                  </div>
                                </div>
                              )}

                              {/* 收藏按钮 */}
                              <div className="relative btn-tooltip">
                                <button
                                  onClick={() => toggleFavorite(item.id)}
                                  className="p-3 rounded-full backdrop-blur-2xl transition-all duration-300 hover:scale-110 border border-white/50"
                                  style={{
                                    background: "rgba(255, 255, 255, 0.85)",
                                    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9)",
                                  }}
                                >
                                  <Heart
                                    className={`w-5 h-5 transition-colors ${
                                      item.isFavorite ? "fill-pink-400 text-pink-400" : "text-gray-400"
                                    }`}
                                  />
                                </button>
                                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-2 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                                  <div className="font-medium text-gray-800">{item.isFavorite ? "取消收藏" : "收藏"}</div>
                                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-[-1px] border-[6px] border-transparent border-b-white"></div>
                                </div>
                              </div>

                              {/* 删除按钮 */}
                              <div className="relative btn-tooltip">
                                <button
                                  onClick={() => handleDelete(item.id)}
                                  className="p-3 rounded-full backdrop-blur-2xl transition-all duration-300 hover:scale-110 border border-white/50"
                                  style={{
                                    background: "rgba(255, 255, 255, 0.85)",
                                    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9)",
                                  }}
                                >
                                  <Trash2 className="w-5 h-5 text-gray-400" />
                                </button>
                                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-2 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                                  <div className="font-medium text-gray-800">删除</div>
                                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-[-1px] border-[6px] border-transparent border-b-white"></div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* 信息栏 */}
                        <div className="p-5">
                          <div className="flex items-center justify-between mb-2">
                            <div>
                              <p className="text-sm text-gray-600/80">情绪: {item.mood}</p>
                              <p className="text-sm text-gray-600/80 mt-1">风格: {getStyleName(item.style)}</p>
                            </div>
                          </div>
                          {item.quote && (
                            <p className="text-[16px] text-gray-800 mt-2 border-t border-gray-200/50 pt-2">
                              "{item.quote}"
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </Masonry>
                </ResponsiveMasonry>
              )}
            </TabsContent>

            {/* 我的收藏 */}
            <TabsContent value="favorites" className="mt-0">
              {favoriteWallpapers.length === 0 ? (
                <div className="text-center py-20">
                  <Heart className="w-16 h-16 text-gray-300/60 mx-auto mb-4" />
                  <p className="text-gray-400/70">还没有收藏的壁纸</p>
                  <p className="text-sm text-gray-300/60 mt-2">点击壁纸上的爱心图标即可收藏</p>
                </div>
              ) : (
                <ResponsiveMasonry columnsCountBreakPoints={{ 350: 1, 750: 2, 900: 3 }}>
                  <Masonry gutter="1.5rem">
                    {favoriteWallpapers.map((item) => (
                      <div
                        key={item.id}
                        className="group relative rounded-3xl overflow-hidden transition-all duration-300 hover:scale-[1.01] hover:shadow-2xl backdrop-blur-xl"
                        style={{
                          background: "linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85))",
                          boxShadow: "0 10px 30px rgba(251, 194, 235, 0.25), 0 4px 12px rgba(209, 217, 230, 0.3), inset 0 1px 2px rgba(255, 255, 255, 1)",
                        }}
                      >
                        <div className="relative overflow-hidden">
                          <img
                            src={item.image}
                            alt={item.mood}
                            className="w-full h-auto object-cover"
                            style={{ aspectRatio: getDisplayRatio(item.aspect_ratio) }}
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                            <div className="absolute top-4 right-4 flex gap-2">
                              {/* 下载按钮 */}
                              <div className="relative btn-tooltip">
                                <button
                                  onClick={() => handleDownload(item, false)}
                                  className="p-3 rounded-full backdrop-blur-2xl transition-all duration-300 hover:scale-110 border border-white/50"
                                  style={{
                                    background: "rgba(255, 255, 255, 0.85)",
                                    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9)",
                                  }}
                                >
                                  <Download className="w-5 h-5 text-gray-400" />
                                </button>
                                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-2 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                                  <div className="font-medium text-gray-800">下载</div>
                                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-[-1px] border-[6px] border-transparent border-b-white"></div>
                                </div>
                              </div>

                              {/* 超清升级/下载超清按钮 */}
                              {!item.hd_path ? (
                                <div className="relative btn-tooltip">
                                  <button
                                    onClick={() => handleUpgradeHD(item)}
                                    className="p-3 rounded-full backdrop-blur-2xl transition-all duration-300 hover:scale-110 border border-white/50"
                                    style={{
                                      background: "rgba(255, 255, 255, 0.85)",
                                      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9)",
                                    }}
                                  >
                                    <Zap className="w-5 h-5 text-pink-400" />
                                  </button>
                                  <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-2 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                                    <div className="font-medium text-gray-800">超清升级</div>
                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-[-1px] border-[6px] border-transparent border-b-white"></div>
                                  </div>
                                </div>
                              ) : (
                                <div className="relative btn-tooltip">
                                  <button
                                    onClick={() => handleDownload(item, true)}
                                    className="p-3 rounded-full backdrop-blur-2xl transition-all duration-300 hover:scale-110 border border-white/50"
                                    style={{
                                      background: "rgba(255, 255, 255, 0.85)",
                                      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9)",
                                    }}
                                  >
                                    <Download className="w-5 h-5 text-pink-400" />
                                  </button>
                                  <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-2 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                                    <div className="font-medium text-gray-800">下载超清</div>
                                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-[-1px] border-[6px] border-transparent border-b-white"></div>
                                  </div>
                                </div>
                              )}

                              {/* 收藏按钮 */}
                              <div className="relative btn-tooltip">
                                <button
                                  onClick={() => toggleFavorite(item.id)}
                                  className="p-3 rounded-full backdrop-blur-2xl transition-all duration-300 hover:scale-110 border border-white/50"
                                  style={{
                                    background: "rgba(255, 255, 255, 0.85)",
                                    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9)",
                                  }}
                                >
                                  <Heart className="w-5 h-5 fill-pink-400 text-pink-400" />
                                </button>
                                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-2 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                                  <div className="font-medium text-gray-800">取消收藏</div>
                                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-[-1px] border-[6px] border-transparent border-b-white"></div>
                                </div>
                              </div>

                              {/* 删除按钮 */}
                              <div className="relative btn-tooltip">
                                <button
                                  onClick={() => handleDelete(item.id)}
                                  className="p-3 rounded-full backdrop-blur-2xl transition-all duration-300 hover:scale-110 border border-white/50"
                                  style={{
                                    background: "rgba(255, 255, 255, 0.85)",
                                    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.08), inset 0 1px 1px rgba(255, 255, 255, 0.9)",
                                  }}
                                >
                                  <Trash2 className="w-5 h-5 text-gray-400" />
                                </button>
                                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 px-3 py-2 rounded-xl backdrop-blur-xl bg-white/95 border border-pink-200/50 text-xs whitespace-nowrap opacity-0 tooltip-text transition-opacity duration-200 pointer-events-none shadow-xl z-50">
                                  <div className="font-medium text-gray-800">删除</div>
                                  <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-[-1px] border-[6px] border-transparent border-b-white"></div>
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="p-5">
                          <div className="flex items-center justify-between mb-2">
                            <div>
                              <p className="text-sm text-gray-600/80">情绪: {item.mood}</p>
                              <p className="text-sm text-gray-600/80 mt-1">风格: {getStyleName(item.style)}</p>
                            </div>
                          </div>
                          {item.quote && (
                            <p className="text-[16px] text-gray-800 mt-2 border-t border-gray-200/50 pt-2">
                              "{item.quote}"
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </Masonry>
                </ResponsiveMasonry>
              )}
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
