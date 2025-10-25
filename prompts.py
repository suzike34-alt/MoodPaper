"""
MoodPaper - AI 情绪壁纸生成应用
文件名: prompts.py
功能: 心情中心化 Prompt 系统（v2.0）
作者: MoodPaper 团队
最后修改: 2025-10-26

设计原则:
1. 心情优先 - 用户的心情是核心，其他都是辅助
2. 场景化表达 - 将抽象情绪转化为具体可视化场景
3. 简洁有力 - 减少技术堆砌，突出情感表达
4. 智能理解 - 深度理解用户输入，而非简单关键词匹配
"""

from typing import TypedDict, List, Optional, Dict, Tuple
import random
import time


# ========================================
# 核心：心情场景库 (Mood Scene Library)
# ========================================
# 这是最重要的部分！将用户的心情直接转化为具体的视觉场景

MOOD_SCENE_PATTERNS = {
    # 动物相关的心情
    "猫": [
        "a cute fluffy cat peacefully sleeping by the sunny window, warm afternoon light, cozy and serene atmosphere",
        "a playful kitten chasing butterflies in a flower garden, joyful and lively scene",
        "an elegant cat silhouette sitting on the windowsill watching the rain, contemplative mood",
        "a lazy cat stretching in warm sunlight, peaceful and comfortable moment",
    ],

    "狗": [
        "a happy dog running freely in a vast green field, pure joy and freedom",
        "a loyal dog waiting by the window for its owner, warm and touching scene",
        "a playful puppy playing with flowers in the garden, innocent and cheerful",
    ],

    # 自然元素相关
    "花": [
        "beautiful wildflowers blooming in a sunny meadow, cheerful and vibrant atmosphere",
        "delicate cherry blossoms falling gently in the breeze, poetic and romantic mood",
        "a single flower standing tall in the gentle rain, resilient and hopeful",
        "colorful flowers in a dreamy garden, soft focus, enchanting beauty",
    ],

    "星": [
        "a twinkling star shining brightly in the vast night sky, lonely yet beautiful",
        "countless stars scattered across the dark sky, mysterious and dreamy atmosphere",
        "a shooting star streaking across the twilight sky, magical moment, hope and wishes",
        "starlight reflecting on a calm lake surface, serene and peaceful night",
    ],

    "云": [
        "fluffy white clouds drifting peacefully in the blue sky, carefree and light mood",
        "dramatic clouds at sunset, painted in golden and pink hues, breathtaking beauty",
        "soft morning clouds floating gently, fresh and peaceful atmosphere",
    ],

    "海": [
        "calm ocean waves gently lapping the shore, peaceful and meditative mood",
        "vast ocean under the sunset sky, lonely yet grand, contemplative atmosphere",
        "turquoise sea with soft waves, refreshing and tranquil scene",
    ],

    "山": [
        "misty mountains in the early morning, serene and mystical atmosphere",
        "a tiny person standing before majestic mountains, feeling small yet inspired",
        "snow-capped mountain peaks under blue sky, pure and breathtaking beauty",
    ],

    "雨": [
        "gentle rain falling on window glass, cozy indoor atmosphere, peaceful mood",
        "soft raindrops creating ripples in puddles, quiet and contemplative scene",
        "rain in a garden making flowers glisten, fresh and rejuvenating mood",
    ],

    # 日常场景相关
    "咖啡": [
        "a warm cup of coffee on a wooden table by the window, cozy cafe atmosphere, peaceful morning",
        "steam rising from a coffee cup, soft window light, quiet and contemplative moment",
    ],

    "书": [
        "a stack of books by the window with soft sunlight, peaceful reading time, cozy atmosphere",
        "an open book on a table with tea, quiet afternoon, serene and contemplative",
    ],

    "窗": [
        "looking out the window at the rain, cozy indoor scene, contemplative mood",
        "sunlight streaming through the window, dust particles floating in the light, peaceful moment",
        "a silhouette by the window watching the sunset, quiet and reflective atmosphere",
    ],

    # 情绪状态相关的场景
    "孤独": [
        "a lone figure sitting on a hill watching the sunset, solitary yet peaceful",
        "a single tree standing in a vast field, lonely yet strong",
        "an empty swing gently swaying in the breeze, nostalgic and melancholic",
    ],

    "平静": [
        "a peaceful lake reflecting the sky like a mirror, absolutely calm and serene",
        "gentle morning mist over a quiet forest, tranquil and meditative",
        "a person meditating in a zen garden, peaceful and centered",
    ],

    "快乐": [
        "colorful balloons floating in a bright blue sky, joyful and carefree",
        "children playing in a sunny park, pure happiness and innocence",
        "bright flowers dancing in the breeze, cheerful and vibrant",
    ],

    "梦幻": [
        "floating islands in a pastel sky with soft clouds, whimsical and magical",
        "a dreamy garden with glowing flowers and fairy lights, enchanting atmosphere",
        "soft watercolor landscape with ethereal glow, surreal and beautiful",
    ],
}


# 通用心情表达的智能理解
MOOD_EXPRESSIONS = {
    "像": {  # "我像一只猫"、"像云一样"
        "猫": "想要慵懒、自由、舒适的状态",
        "云": "想要轻盈、自由、无忧无虑",
        "星": "想要闪耀、独特、遥远而美丽",
        "花": "想要美丽、绽放、被欣赏",
    },

    "想": {  # "想变成"、"想要"
        "猫": "渴望悠闲自在的生活",
        "云": "渴望自由飘荡",
        "星": "渴望发光发热",
    },

    "看到": {  # "看到花很开心"
        "花": "被美好事物感动",
        "云": "被自然美景治愈",
    },
}


def understand_mood(mood_text: str, selected_style: str) -> str:
    """
    深度理解用户的心情，转化为具体的视觉场景

    这是核心函数！不只是提取关键词，而是真正理解用户想表达什么
    """
    mood_text = mood_text.strip()

    # 1. 先尝试从场景库中找到直接匹配
    for keyword, scenes in MOOD_SCENE_PATTERNS.items():
        if keyword in mood_text:
            # 找到了关键词，选择一个场景
            base_scene = random.choice(scenes)

            # 根据具体表达方式调整场景
            if "像" in mood_text and keyword == "猫":
                # "我像一只猫" - 强调慵懒、舒适的状态
                base_scene = "a cute fluffy cat peacefully sleeping by the sunny window, warm afternoon light, cozy and serene atmosphere, lazy and content mood"
            elif "想变成" in mood_text or "想成为" in mood_text:
                # "想变成星星" - 强调向往、梦想
                if keyword == "星":
                    base_scene = "a beautiful twinkling star shining brightly in the vast night sky, dreamy atmosphere, hope and wishes, magical glow"
                elif keyword == "云":
                    base_scene = "soft fluffy clouds floating freely in the endless blue sky, carefree and light, freedom and peace"
            elif "看到" in mood_text and "开心" in mood_text:
                # "看到花很开心" - 强调喜悦、被美好事物感动
                if keyword == "花":
                    base_scene = "beautiful colorful flowers blooming brightly in a sunny garden, joyful and cheerful atmosphere, happiness and delight, vibrant petals"

            return base_scene

    # 2. 如果没有找到具体元素，根据情绪生成通用场景
    if "开心" in mood_text or "快乐" in mood_text or "高兴" in mood_text:
        return "a bright and cheerful scene with warm sunlight and soft colors, joyful atmosphere, happy mood"
    elif "平静" in mood_text or "安静" in mood_text or "放松" in mood_text:
        return "a peaceful and serene scene with soft natural light, calm atmosphere, tranquil mood"
    elif "孤独" in mood_text or "寂寞" in mood_text:
        return "a solitary scene with vast empty space, contemplative atmosphere, quiet and introspective mood"
    elif "难过" in mood_text or "伤心" in mood_text:
        return "a gentle melancholic scene with soft muted colors, comforting atmosphere, wistful mood"
    elif "兴奋" in mood_text or "激动" in mood_text:
        return "an energetic and vibrant scene with dynamic elements, exciting atmosphere, lively mood"
    elif "梦幻" in mood_text or "奇幻" in mood_text:
        return "a dreamy ethereal scene with soft glowing lights, magical atmosphere, whimsical mood"
    else:
        # 默认：温和、治愈的场景
        return "a warm and gentle scene with soft natural light, peaceful atmosphere, cozy and comforting mood"


# ========================================
# 风格配置（简化版 - 只保留核心修饰）
# ========================================

class StyleConfig(TypedDict):
    name: str
    core_modifiers: List[str]  # 核心修饰词（2-3个即可）
    art_style: List[str]  # 艺术风格（1-2个）
    quality_params: str  # 画质参数（精简）
    negative: str


STYLE_CONFIGS: Dict[str, StyleConfig] = {
    # 🌸 疗愈系
    "healing": {
        "name": "🌸 疗愈",
        "core_modifiers": [
            "soft pastel colors",
            "warm gentle lighting",
            "cozy atmosphere",
            "healing vibe",
            "delicate details",
        ],
        "art_style": [
            "watercolor painting style",
            "hand-drawn illustration",
            "Miyazaki Hayao illustration style",
            "soft dreamy art style",
            "gentle storybook illustration",
        ],
        "quality_params": "high quality, beautiful details, masterpiece",
        "negative": "ugly, dark, gloomy, harsh, scary, photorealistic, photo, photography"
    },

    # ⚡ 能量系
    "energetic": {
        "name": "⚡ 能量",
        "core_modifiers": [
            "vibrant bold colors",
            "dynamic composition",
            "energetic atmosphere",
            "bright lighting",
            "lively mood",
        ],
        "art_style": [
            "vibrant illustration style",
            "colorful digital art",
            "pop art influence",
            "dynamic art style",
        ],
        "quality_params": "high quality, vivid colors, masterpiece",
        "negative": "ugly, dull, boring, lifeless, dark, gloomy"
    },

    # 🌙 梦幻系
    "dreamy": {
        "name": "🌙 梦幻",
        "core_modifiers": [
            "dreamy soft focus",
            "ethereal glow",
            "magical atmosphere",
            "whimsical elements",
            "pastel iridescent colors",
        ],
        "art_style": [
            "fantasy illustration style",
            "dreamy watercolor",
            "ethereal art style",
            "magical painting style",
        ],
        "quality_params": "high quality, enchanting beauty, masterpiece",
        "negative": "ugly, realistic, mundane, harsh, dark, scary, photorealistic"
    },

    # 🎯 极简系
    "minimalist": {
        "name": "🎯 极简",
        "core_modifiers": [
            "clean simple composition",
            "minimal elements",
            "negative space",
            "zen aesthetic",
            "subtle colors",
        ],
        "art_style": [
            "minimalist art style",
            "simple illustration",
            "zen painting style",
            "clean modern art",
        ],
        "quality_params": "high quality, elegant simplicity, masterpiece",
        "negative": "ugly, cluttered, busy, complex, chaotic, messy"
    },

    # 🌿 自然系
    "natural": {
        "name": "🌿 自然",
        "core_modifiers": [
            "natural lighting",
            "organic earthy tones",
            "serene atmosphere",
            "breathtaking scenery",
            "tranquil mood",
        ],
        "art_style": [
            "landscape photography style",
            "cinematic natural scene",
            "nature photography aesthetic",
            "fine art landscape",
        ],
        "quality_params": "high quality, stunning natural beauty, masterpiece",
        "negative": "ugly, artificial, urban, industrial, mechanical, man-made"
    }
}


# ========================================
# 核心 Prompt 生成函数（简化重构版）
# ========================================

def build_wallpaper_prompt(mood_keyword: str, selected_style: str) -> Tuple[str, str]:
    """
    生成以心情为中心的高质量 Wallpaper Prompt

    新的结构（简洁有力）：
    1. 核心心情场景（最重要！占70%权重）
    2. 风格修饰词（20%权重）
    3. 艺术风格（5%权重）
    4. 画质参数（5%权重）

    Args:
        mood_keyword: 用户输入的心情关键词
        selected_style: 用户选择的壁纸风格

    Returns:
        (positive_prompt, negative_prompt)
    """
    if selected_style not in STYLE_CONFIGS:
        raise ValueError(f"不支持的风格: {selected_style}")

    # 初始化随机种子
    random.seed(int(time.time() * 1000))

    style_config = STYLE_CONFIGS[selected_style]

    # ========== 第一步：理解并生成核心心情场景（最重要！）==========
    mood_scene = understand_mood(mood_keyword, selected_style)

    # ========== 第二步：添加风格修饰（精选2个）==========
    style_modifiers = random.sample(style_config["core_modifiers"],
                                   min(2, len(style_config["core_modifiers"])))

    # ========== 第三步：添加艺术风格（只选1个）==========
    art_style = random.choice(style_config["art_style"])

    # ========== 第四步：画质参数（简洁版）==========
    quality = style_config["quality_params"]

    # ========== 组合最终 Prompt（心情场景放在最前面！）==========
    parts = [
        mood_scene,  # 核心场景（最重要）
        ", ".join(style_modifiers),  # 风格修饰
        art_style,  # 艺术风格
        quality,  # 画质参数
    ]

    final_prompt = ", ".join(parts)
    negative_prompt = style_config["negative"]

    # 重置随机种子
    random.seed()

    return final_prompt, negative_prompt


# ========================================
# 签文生成（保持不变）
# ========================================

def build_quote_prompt(mood_keyword: str) -> str:
    """生成签文 Prompt"""
    return (
        f"用户现在的心情是：{mood_keyword}。"
        f"请生成一句15字以内的温暖治愈签文，要符合年轻女性的语言风格，"
        f"温柔、真诚、有共鸣感，像朋友般的关心。"
        f"直接输出签文，不要引号或说明。"
    )


# ========================================
# 辅助函数
# ========================================

SUPPORTED_STYLES = list(STYLE_CONFIGS.keys())

STYLE_DISPLAY_NAMES = {
    style_key: style_config["name"]
    for style_key, style_config in STYLE_CONFIGS.items()
}


def get_style_name(selected_style: str) -> str:
    return STYLE_DISPLAY_NAMES.get(selected_style, selected_style)


def validate_style(selected_style: str) -> bool:
    return selected_style in SUPPORTED_STYLES


# ========================================
# 测试
# ========================================

if __name__ == "__main__":
    test_cases = [
        ("我像一只猫", "healing"),
        ("看到花很开心", "healing"),
        ("想变成一颗星星", "dreamy"),
        ("充满活力", "energetic"),
        ("平静的海", "natural"),
        ("简单就好", "minimalist"),
        ("今天很孤独", "healing"),
        ("想要自由", "dreamy"),
    ]

    print("\n" + "=" * 120)
    print("心情中心化 Prompt 系统测试（v2.0 - 简洁有力版）")
    print("=" * 120 + "\n")

    for mood, style in test_cases:
        print(f"心情: {mood} | 风格: {style}")
        print("-" * 120)

        prompt, negative = build_wallpaper_prompt(mood, style)

        print(f"正向 Prompt:\n{prompt}\n")
        print(f"负向 Prompt:\n{negative}\n")
        print("=" * 120 + "\n")
