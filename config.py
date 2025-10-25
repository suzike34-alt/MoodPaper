"""
MoodPaper - AI 情绪壁纸生成应用
文件名: config.py
功能: 配置管理
作者: MoodPaper 团队
创建日期: 2025-10-24
最后修改: 2025-10-24

主要功能:
1. 加载环境变量
2. 管理 API 配置
3. 定义应用常量
4. 提供配置验证
"""

import os
from dotenv import load_dotenv


# ========== 加载环境变量 ==========

# 从 .env 文件加载环境变量（如果文件存在）
load_dotenv()


# ========== API 配置 ==========

# OpenRouter API Key（从环境变量读取）
# 注意：OpenRouter 的 API Key 格式通常以 sk-or-v1- 开头
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")

# OpenRouter API 基础 URL
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

# 应用信息（OpenRouter 推荐在请求头中提供）
APP_NAME: str = "MoodPaper"
APP_URL: str = "https://github.com/yourusername/moodpaper"  # 可以修改为实际仓库地址


# ========== 模型配置 ==========

# 文本生成模型（用于生成疗愈签文）
# OpenRouter 支持多种模型,可以根据需要更换
TEXT_GENERATION_MODEL: str = "anthropic/claude-3.5-sonnet"  # Claude 3.5 Sonnet（推荐）
# 其他选项:
# - "openai/gpt-4-turbo"
# - "openai/gpt-3.5-turbo"
# - "meta-llama/llama-3.1-70b-instruct"

# 图像生成模型（用于生成壁纸）
# 使用 Stability AI 作为主要方案（性价比最高）
IMAGE_GENERATION_MODEL: str = "stability-ai"  # 使用 Stability AI

# 通义万相 API Key（推荐，阿里云图像生成服务）
TONGYI_API_KEY: str = os.getenv("TONGYI_API_KEY", "")

# 通义万相配置
TONGYI_API_HOST: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
TONGYI_MODEL: str = "wanx-v1"  # 通义万相模型版本

# Stability AI API Key（备选方案1）
STABILITY_API_KEY: str = os.getenv("STABILITY_API_KEY", "")

# Stability AI 配置
STABILITY_ENGINE: str = "stable-diffusion-xl-1024-v1-0"  # SDXL 模型
STABILITY_API_HOST: str = "https://api.stability.ai"

# 备选方案2：Replicate（可选）
REPLICATE_API_TOKEN: str = os.getenv("REPLICATE_API_TOKEN", "")

# ⚠️ 备选方案已禁用（成本原因）
# 为了节省成本，只使用通义万相作为唯一的图像生成服务
# 如需启用备选方案，请将以下标志改为 True，并在 utils.py 中取消相应代码的注释
USE_STABILITY_FALLBACK: bool = False  # 已禁用 Stability AI 备选方案
USE_REPLICATE_FALLBACK: bool = False  # 已禁用 Replicate 备选方案


# ========== 生成参数配置 ==========

# 图像生成参数
IMAGE_WIDTH: int = 1024     # 图像宽度（像素）
IMAGE_HEIGHT: int = 1024    # 图像高度（像素）
# 注意：4K (3840x2160) 可能不被所有模型支持,使用 1024x1024 作为标准尺寸

# 文本生成参数
TEXT_MAX_TOKENS: int = 100          # 最大生成 token 数
TEXT_TEMPERATURE: float = 0.9       # 温度参数（0-2,越高越有创意）
MAX_QUOTE_LENGTH: int = 15          # 签文最大长度（字符数）

# API 调用参数
API_TIMEOUT: int = 120              # API 超时时间（秒）
MAX_RETRY_COUNT: int = 3            # 最大重试次数


# ========== 缓存配置 ==========

# 使用绝对路径确保从任何目录运行都能找到
import sys
_current_dir = os.path.dirname(os.path.abspath(__file__))

# 图片输出目录（用于保存生成的壁纸）
OUTPUT_DIR: str = os.path.join(_current_dir, "output")

# 数据缓存目录（用于保存配额、历史等数据）
CACHE_DIR: str = os.path.join(_current_dir, "cache")

# 默认值配置
DEFAULT_STYLE: str = "healing"              # 默认风格
DEFAULT_QUOTE: str = "每一个当下,都值得温柔以待。"  # 默认签文（生成失败时使用）


# ========== 配置验证函数 ==========

def validate_api_config() -> tuple[bool, str]:
    """
    验证 API 配置是否完整和正确

    检查必要的 API Key 是否已配置,格式是否正确。

    Returns:
        tuple[bool, str]: (是否有效, 错误信息)
        - 如果配置有效: (True, "")
        - 如果配置无效: (False, "错误描述")

    Example:
        >>> is_valid, error_msg = validate_api_config()
        >>> if not is_valid:
        ...     print(f"配置错误: {error_msg}")
    """
    # === 检查 OpenRouter API Key ===
    if not OPENROUTER_API_KEY:
        return False, "未配置 OPENROUTER_API_KEY,请在 .env 文件中添加"

    # === 检查 API Key 格式 ===
    # OpenRouter 的 API Key 通常以 sk-or-v1- 开头
    if not OPENROUTER_API_KEY.startswith("sk-"):
        return False, "OPENROUTER_API_KEY 格式不正确,应该以 sk- 开头"

    # === 配置有效 ===
    return True, ""


def get_api_headers() -> dict[str, str]:
    """
    获取 API 请求头

    构建 OpenRouter API 调用所需的请求头,包括认证和应用信息。

    Returns:
        dict[str, str]: HTTP 请求头字典

    Example:
        >>> headers = get_api_headers()
        >>> print(headers["Authorization"])
        "Bearer sk-or-v1-..."
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": APP_URL,      # OpenRouter 推荐添加
        "X-Title": APP_NAME            # OpenRouter 推荐添加
    }
    return headers


def get_config_summary() -> dict[str, str]:
    """
    获取配置摘要（用于调试和日志）

    返回当前配置的摘要信息,但不包含敏感的 API Key。

    Returns:
        dict[str, str]: 配置摘要字典

    Example:
        >>> summary = get_config_summary()
        >>> print(summary)
        {
            'text_model': 'anthropic/claude-3.5-sonnet',
            'api_configured': '是',
            'base_url': 'https://openrouter.ai/api/v1'
        }
    """
    return {
        "text_model": TEXT_GENERATION_MODEL,
        "image_model": IMAGE_GENERATION_MODEL,
        "api_configured": "是" if OPENROUTER_API_KEY else "否",
        "replicate_configured": "是" if REPLICATE_API_TOKEN else "否",
        "base_url": OPENROUTER_BASE_URL,
        "output_dir": OUTPUT_DIR,
        "cache_dir": CACHE_DIR
    }


# ========== 环境检查函数 ==========

def check_environment() -> dict[str, bool]:
    """
    检查运行环境

    检查所有必要的配置和依赖是否就绪。

    Returns:
        dict[str, bool]: 各项检查结果
        {
            "openrouter_key": True/False,
            "replicate_key": True/False,
            "output_dir_exists": True/False,
            "cache_dir_exists": True/False
        }

    Example:
        >>> env_check = check_environment()
        >>> if all(env_check.values()):
        ...     print("环境检查通过!")
    """
    # 检查 OpenRouter API Key
    has_openrouter_key = bool(OPENROUTER_API_KEY)

    # 检查 Replicate API Token（备选方案）
    has_replicate_key = bool(REPLICATE_API_TOKEN)

    # 检查输出目录是否存在
    output_dir_exists = os.path.exists(OUTPUT_DIR)

    # 检查缓存目录是否存在
    cache_dir_exists = os.path.exists(CACHE_DIR)

    return {
        "openrouter_key": has_openrouter_key,
        "replicate_key": has_replicate_key,
        "output_dir_exists": output_dir_exists,
        "cache_dir_exists": cache_dir_exists
    }


# ========== 初始化操作 ==========

def initialize_cache_dir() -> bool:
    """
    初始化缓存和输出目录

    如果目录不存在,创建它们。

    Returns:
        bool: 是否成功创建或已存在

    Example:
        >>> success = initialize_cache_dir()
        >>> print(f"目录就绪: {success}")
    """
    try:
        # 创建输出目录（壁纸图片）
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
            print(f"✅ 创建输出目录: {OUTPUT_DIR}")

        # 创建缓存目录（数据文件）
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
            print(f"✅ 创建缓存目录: {CACHE_DIR}")

        return True
    except Exception as e:
        print(f"❌ 创建目录失败: {e}")
        return False
