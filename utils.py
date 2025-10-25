"""
MoodPaper - AI 情绪壁纸生成应用
文件名: utils.py
功能: 工具函数（API 调用、图像处理）
作者: MoodPaper 团队
创建日期: 2025-10-24
最后修改: 2025-10-24

主要功能:
1. OpenRouter API 调用封装
2. 图像生成功能
3. 文本生成功能
4. 错误处理和重试机制
"""

import os
import requests
import time
from typing import Optional

# 导入配置
from config import (
    OPENROUTER_BASE_URL,
    TEXT_GENERATION_MODEL,
    IMAGE_GENERATION_MODEL,
    TEXT_MAX_TOKENS,
    TEXT_TEMPERATURE,
    API_TIMEOUT,
    MAX_RETRY_COUNT,
    DEFAULT_QUOTE,
    TONGYI_API_KEY,
    TONGYI_API_HOST,
    TONGYI_MODEL,
    STABILITY_API_KEY,
    STABILITY_ENGINE,
    STABILITY_API_HOST,
    REPLICATE_API_TOKEN,
    USE_STABILITY_FALLBACK,
    USE_REPLICATE_FALLBACK,
    get_api_headers
)

# 导入 Prompt 构建函数
from prompts import build_wallpaper_prompt, build_quote_prompt


# ========== OpenRouter API 调用封装 ==========

def call_openrouter_text_api(
    prompt: str,
    model: str = TEXT_GENERATION_MODEL,
    max_tokens: int = TEXT_MAX_TOKENS,
    temperature: float = TEXT_TEMPERATURE
) -> Optional[str]:
    """
    调用 OpenRouter 文本生成 API

    向 OpenRouter 发送请求,生成文本内容。
    包含自动重试机制和错误处理。

    Args:
        prompt: 提示词内容
        model: 要使用的模型名称
        max_tokens: 最大生成 token 数
        temperature: 温度参数（0-2,越高越有创意）

    Returns:
        Optional[str]: 生成的文本,失败返回 None

    Example:
        >>> text = call_openrouter_text_api("生成一句励志名言")
        >>> print(text)
        "每一天都是新的开始。"
    """
    # === 第一步: 准备请求参数 ===
    headers = get_api_headers()

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    # === 第二步: 发送请求（带重试机制）===
    for attempt in range(MAX_RETRY_COUNT):
        try:
            response = requests.post(
                f"{OPENROUTER_BASE_URL}/chat/completions",
                headers=headers,
                json=payload,
                timeout=API_TIMEOUT
            )

            # 检查 HTTP 状态码
            response.raise_for_status()

            # 解析响应
            result = response.json()

            # 提取生成的文本
            if "choices" in result and len(result["choices"]) > 0:
                generated_text = result["choices"][0]["message"]["content"]
                return generated_text.strip()

            # 响应格式异常
            print(f"⚠️ API 响应格式异常: {result}")
            return None

        except requests.Timeout:
            # 超时错误 - 重试
            print(f"⏰ API 调用超时 (尝试 {attempt + 1}/{MAX_RETRY_COUNT})")
            if attempt < MAX_RETRY_COUNT - 1:
                time.sleep(2 ** attempt)  # 指数退避
                continue
            else:
                print("❌ API 调用超时,已达最大重试次数")
                return None

        except requests.RequestException as e:
            # 网络或 API 错误
            print(f"🔴 API 调用失败: {str(e)}")
            return None

        except Exception as e:
            # 其他未知错误
            print(f"❌ 未知错误: {str(e)}")
            return None

    return None


# ========== 图像生成函数 ==========

def generate_wallpaper(mood_keyword: str, selected_style: str, aspect_ratio: str = "9:16", is_hd: bool = False) -> Optional[str]:
    """
    生成 AI 壁纸

    根据用户的心情关键词和选择的风格,调用通义万相 API 生成壁纸图片。

    Args:
        mood_keyword: 心情关键词,如 "焦虑"、"快乐"、"平静"
        selected_style: 风格键名,必须是 SUPPORTED_STYLES 中的一个
                       ("healing", "energetic", "dreamy", "minimalist", "nature")
        aspect_ratio: 图片比例 ("1:1", "16:9", "9:16")
        is_hd: 是否生成超清版本 (默认 False)

    Returns:
        Optional[str]: 生成的图片本地路径,失败返回 None

    Raises:
        ValueError: 当 selected_style 不在支持列表中时

    Example:
        >>> image_url = generate_wallpaper("焦虑", "healing", "9:16")
        >>> if image_url:
        ...     print(f"图片地址: {image_url}")
    """
    # === 第一步: 验证输入 ===
    if not mood_keyword:
        print("❌ 心情关键词不能为空")
        return None

    # === 第二步: 构建 Prompt ===
    try:
        wallpaper_prompt, negative_prompt = build_wallpaper_prompt(
            mood_keyword,
            selected_style
        )
    except ValueError as e:
        print(f"❌ Prompt 构建失败: {str(e)}")
        return None

    # === 第三步: 使用通义万相生成图像 ===
    quality_text = "超清" if is_hd else "标清"
    print(f"🎨 正在使用通义万相生成{quality_text}壁纸（比例：{aspect_ratio}）...")
    image_url = generate_wallpaper_with_tongyi(wallpaper_prompt, negative_prompt, aspect_ratio, is_hd)

    if image_url:
        print(f"✅ 通义万相{quality_text}图像生成成功")
        return image_url
    else:
        print(f"❌ 通义万相{quality_text}图像生成失败")
        print("💡 提示：请检查 TONGYI_API_KEY 配置是否正确，或稍后重试")
        return None


def generate_wallpaper_with_tongyi(prompt: str, negative_prompt: str, aspect_ratio: str = "9:16", is_hd: bool = False) -> Optional[str]:
    """
    使用阿里云通义万相生成壁纸（优先方案）

    调用阿里云通义万相 API 生成高质量壁纸。
    优势：便宜（¥0.06/张），新用户有 500 张免费额度，国内访问速度快。

    Args:
        prompt: 图像生成提示词
        negative_prompt: 负面提示词
        aspect_ratio: 图片比例 ("1:1", "16:9", "9:16")
        is_hd: 是否生成超清版本 (默认 False)

    Returns:
        Optional[str]: 生成的图片本地路径，失败返回 None
    """
    try:
        # === 第一步: 检查 API Key ===
        if not TONGYI_API_KEY:
            print("⚠️ 未配置 TONGYI_API_KEY")
            print("提示: 访问 https://bailian.console.aliyun.com 申请 API Key")
            return None

        # === 第二步: 准备请求 ===
        import json

        headers = {
            "Authorization": f"Bearer {TONGYI_API_KEY}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable"  # 使用异步模式
        }

        # 通义万相支持的分辨率格式（根据比例和是否超清映射）
        if is_hd:
            # 超清版本
            # 注意：通义万相对不同比例支持的最高分辨率不同
            size_map_hd = {
                "1:1": "2048*2048",     # 支持 2K 超清
                "16:9": "1280*720",     # 暂无更高分辨率
                "9:16": "720*1280"      # 暂无更高分辨率
            }
            size = size_map_hd.get(aspect_ratio, "2048*2048")

            # 如果是 16:9 或 9:16，提示用户暂无超清版本
            if aspect_ratio in ["16:9", "9:16"]:
                print(f"⚠️ 通义万相暂不支持 {aspect_ratio} 比例的超清版本")
                print(f"💡 将生成相同分辨率的新图片")
        else:
            # 标清版本
            size_map = {
                "1:1": "1024*1024",
                "16:9": "1280*720",
                "9:16": "720*1280"
            }
            size = size_map.get(aspect_ratio, "720*1280")  # 默认 9:16

        # 构建请求体
        payload = {
            "model": TONGYI_MODEL,
            "input": {
                "prompt": prompt,
                "negative_prompt": negative_prompt
            },
            "parameters": {
                "size": size,
                "n": 1  # 生成1张图片
            }
        }

        # === 第三步: 发送请求（异步）===
        response = requests.post(
            TONGYI_API_HOST,
            headers=headers,
            json=payload,
            timeout=10
        )

        # === 第四步: 处理响应 ===
        if response.status_code == 200:
            result = response.json()

            # 通义万相使用异步模式，需要获取 task_id 然后轮询结果
            if "output" in result and "task_id" in result["output"]:
                task_id = result["output"]["task_id"]
                print(f"📝 任务ID: {task_id}，等待生成...")

                # 轮询任务状态
                image_url = poll_tongyi_task(task_id)

                if image_url:
                    # 下载图片到本地
                    return download_tongyi_image(image_url, prompt)

        else:
            error_msg = response.text
            print(f"❌ 通义万相 API 错误: HTTP {response.status_code}")
            print(f"   错误详情: {error_msg}")
            return None

    except Exception as e:
        print(f"❌ 通义万相生成异常: {str(e)}")
        return None


def poll_tongyi_task(task_id: str, max_wait: int = 120) -> Optional[str]:
    """
    轮询通义万相任务状态

    Args:
        task_id: 任务ID
        max_wait: 最大等待时间（秒）

    Returns:
        Optional[str]: 图片URL，失败返回 None
    """
    try:
        headers = {
            "Authorization": f"Bearer {TONGYI_API_KEY}"
        }

        # 任务查询URL
        task_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"

        # 轮询（每2秒查询一次）
        start_time = time.time()
        while time.time() - start_time < max_wait:
            response = requests.get(task_url, headers=headers, timeout=10)

            if response.status_code == 200:
                result = response.json()

                # 检查任务状态
                if "output" in result:
                    task_status = result["output"].get("task_status", "")

                    if task_status == "SUCCEEDED":
                        # 任务成功，获取图片URL
                        results = result["output"].get("results", [])
                        if results and len(results) > 0:
                            return results[0].get("url")

                    elif task_status == "FAILED":
                        error_msg = result.get('message', '未知错误')
                        error_code = result.get('code', '')
                        print(f"❌ 通义万相任务失败: {error_msg} (code: {error_code})")
                        print(f"   完整响应: {result}")
                        return None

                    # 状态为 PENDING 或 RUNNING，继续等待
                    print(f"⏳ 生成中... ({task_status})")

            time.sleep(2)  # 等待2秒后再次查询

        print("❌ 通义万相任务超时")
        return None

    except Exception as e:
        print(f"❌ 轮询任务状态失败: {str(e)}")
        return None


def download_tongyi_image(image_url: str, prompt: str) -> Optional[str]:
    """
    下载通义万相生成的图片到本地

    Args:
        image_url: 图片URL
        prompt: 提示词（用于生成文件名）

    Returns:
        Optional[str]: 本地文件路径，失败返回 None
    """
    try:
        # 下载图片
        response = requests.get(image_url, timeout=30)

        if response.status_code == 200:
            # 保存到输出目录
            from config import OUTPUT_DIR, initialize_cache_dir
            initialize_cache_dir()

            import hashlib

            # 生成唯一文件名
            timestamp = int(time.time())
            hash_str = hashlib.md5(prompt.encode()).hexdigest()[:8]
            filename = f"tongyi_{timestamp}_{hash_str}.png"
            filepath = os.path.join(OUTPUT_DIR, filename)

            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(response.content)

            print(f"✅ 图片已保存: {filepath}")
            return filepath
        else:
            print(f"❌ 下载图片失败: HTTP {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ 下载图片异常: {str(e)}")
        return None


def generate_wallpaper_with_stability(prompt: str, resolution: int = 1024) -> Optional[str]:
    """
    使用 Stability AI 生成壁纸（已禁用 - 成本原因）

    ⚠️ 此功能已被禁用以节省成本。
    如需启用，请在 generate_wallpaper() 函数中添加相应的调用逻辑。

    调用 Stability AI 的 Stable Diffusion XL 模型生成高质量壁纸。
    支持小公司免费使用。

    Args:
        prompt: 图像生成提示词
        resolution: 分辨率（1024或2048）

    Returns:
        Optional[str]: 生成的图片 URL 或 base64,失败返回 None
    """
    try:
        # === 第一步: 检查 API Key ===
        if not STABILITY_API_KEY:
            print("⚠️ 未配置 STABILITY_API_KEY")
            return None

        # === 第二步: 准备请求 ===
        import base64
        import io
        from PIL import Image as PILImage

        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # 根据分辨率调整推理步数（Stability AI 最大 50 步）
        steps = 50

        # 构建请求体
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7.5,      # 引导强度
            "height": resolution,  # 高度
            "width": resolution,   # 宽度
            "samples": 1,          # 生成数量
            "steps": steps         # 推理步数（超清增加步数）
        }

        # === 第三步: 发送请求 ===
        response = requests.post(
            f"{STABILITY_API_HOST}/v1/generation/{STABILITY_ENGINE}/text-to-image",
            headers=headers,
            json=payload,
            timeout=180  # 3分钟超时
        )

        # === 第四步: 处理响应 ===
        if response.status_code == 200:
            result = response.json()

            # Stability AI 返回 base64 图像
            if "artifacts" in result and len(result["artifacts"]) > 0:
                image_data = result["artifacts"][0]

                if "base64" in image_data:
                    # 将 base64 转换为图片并保存到临时文件
                    image_b64 = image_data["base64"]
                    image_bytes = base64.b64decode(image_b64)

                    # 保存到输出目录
                    from config import OUTPUT_DIR, initialize_cache_dir
                    initialize_cache_dir()

                    import hashlib
                    import time

                    # 生成唯一文件名
                    timestamp = int(time.time())
                    hash_str = hashlib.md5(prompt.encode()).hexdigest()[:8]
                    filename = f"stability_{timestamp}_{hash_str}.png"
                    filepath = os.path.join(OUTPUT_DIR, filename)

                    # 保存图片
                    img = PILImage.open(io.BytesIO(image_bytes))
                    img.save(filepath, "PNG")

                    print(f"✅ 图片已保存: {filepath}")

                    # 返回本地文件路径（Streamlit 可以显示）
                    return filepath

        else:
            error_msg = response.text
            print(f"❌ Stability AI API 错误: HTTP {response.status_code}")
            print(f"   错误详情: {error_msg}")
            return None

    except Exception as e:
        print(f"❌ Stability AI 生成异常: {str(e)}")
        return None


def generate_wallpaper_with_openrouter(prompt: str) -> Optional[str]:
    """
    使用 OpenRouter API 生成壁纸（主要方案）

    调用 OpenRouter 的图像生成模型创建壁纸。
    支持多种模型,包括 Gemini, GPT-4o 等。

    Args:
        prompt: 图像生成提示词

    Returns:
        Optional[str]: 生成的图片 URL,失败返回 None
    """
    try:
        # === 第一步: 准备请求参数 ===
        headers = get_api_headers()

        # 构建图像生成请求
        # OpenRouter 的图像生成使用特定的消息格式
        payload = {
            "model": IMAGE_GENERATION_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": f"Generate an image: {prompt}"
                }
            ],
            # 某些模型可能需要这个参数
            "max_tokens": 1000
        }

        # === 第二步: 发送请求 ===
        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=180  # 图像生成可能需要更长时间
        )

        # 检查响应状态
        response.raise_for_status()
        result = response.json()

        # === 第三步: 提取图像数据 ===
        # OpenRouter 返回格式可能因模型而异
        # 尝试多种可能的响应格式

        # 格式 1: 图像在 choices[0].message.content 中
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"].get("content", "")

            # 检查是否包含图像 URL
            if content and ("http://" in content or "https://" in content):
                # 从文本中提取 URL
                import re
                urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', content)
                if urls:
                    return urls[0]

            # 格式 2: 可能返回 base64 图像数据
            # 这种情况需要上传到临时存储或转换为 data URL
            # 暂时不支持,返回 None

        # === 第四步: 如果上述格式都不匹配,返回 None ===
        print(f"⚠️ OpenRouter 响应格式不支持: {result}")
        return None

    except requests.RequestException as e:
        print(f"⚠️ OpenRouter API 调用失败: {str(e)}")
        return None
    except Exception as e:
        print(f"⚠️ OpenRouter 图像生成错误: {str(e)}")
        return None


def generate_wallpaper_with_replicate(prompt: str, resolution: int = 1024) -> Optional[str]:
    """
    使用 Replicate API 生成壁纸（已禁用 - 成本原因）

    ⚠️ 此功能已被禁用以节省成本。
    如需启用，请在 generate_wallpaper() 函数中添加相应的调用逻辑。

    当 OpenRouter 不支持图像生成时,使用 Replicate 作为备选方案。

    Args:
        prompt: 图像生成提示词
        resolution: 分辨率（1024或2048）

    Returns:
        Optional[str]: 生成的图片 URL,失败返回 None
    """
    # === 检查 Replicate API Token ===
    if not REPLICATE_API_TOKEN:
        print("⚠️ 未配置 REPLICATE_API_TOKEN")
        print("提示: 在 .env 文件中添加 REPLICATE_API_TOKEN=r8_xxx")
        return None

    # === 调用 Replicate API ===
    try:
        import replicate

        # 根据分辨率调整推理步数（Stability AI 最大 50 步）
        steps = 50

        # 使用 Stable Diffusion XL 模型生成图片
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": prompt,
                "width": resolution,        # 根据参数调整
                "height": resolution,
                "num_outputs": 1,           # 生成 1 张图片
                "guidance_scale": 7.5,      # 引导强度
                "num_inference_steps": steps  # 推理步数
            }
        )

        # 返回生成的图片 URL
        if output and len(output) > 0:
            return output[0]
        else:
            print("❌ Replicate API 未返回图片")
            return None

    except ImportError:
        print("❌ 未安装 replicate 包")
        print("提示: 运行 pip install replicate")
        return None

    except Exception as e:
        print(f"❌ Replicate API 调用失败: {str(e)}")
        return None


# ========== 文本生成函数 ==========

def generate_quote(mood_keyword: str) -> str:
    """
    生成疗愈签文

    根据用户的心情关键词,调用 OpenRouter API 生成温暖治愈的短签文。

    Args:
        mood_keyword: 心情关键词,如 "焦虑"、"快乐"、"平静"

    Returns:
        str: 生成的签文,失败时返回默认签文

    Example:
        >>> quote = generate_quote("焦虑")
        >>> print(quote)
        "深呼吸,一切都会好起来的。"
    """
    # === 第一步: 验证输入 ===
    if not mood_keyword:
        return DEFAULT_QUOTE

    # === 第二步: 构建 Prompt ===
    quote_prompt = build_quote_prompt(mood_keyword)

    # === 第三步: 调用 OpenRouter API 生成签文 ===
    print("✍️ 正在生成签文...")

    generated_quote = call_openrouter_text_api(
        prompt=quote_prompt,
        model=TEXT_GENERATION_MODEL,
        max_tokens=TEXT_MAX_TOKENS,
        temperature=TEXT_TEMPERATURE
    )

    # === 第四步: 处理生成结果 ===
    if generated_quote:
        # 移除可能的引号
        generated_quote = generated_quote.strip('"').strip("'").strip('"').strip('"')
        return generated_quote
    else:
        # 生成失败,返回默认签文
        print("⚠️ 签文生成失败,使用默认签文")
        return DEFAULT_QUOTE


# ========== 辅助函数 ==========

def test_api_connection() -> bool:
    """
    测试 API 连接是否正常

    发送一个简单的测试请求,检查 API 是否可用。

    Returns:
        bool: 连接是否正常

    Example:
        >>> is_connected = test_api_connection()
        >>> if is_connected:
        ...     print("API 连接正常")
    """
    try:
        headers = get_api_headers()

        # 发送一个简单的测试请求
        test_prompt = "你好"

        payload = {
            "model": TEXT_GENERATION_MODEL,
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": 10
        }

        response = requests.post(
            f"{OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=10
        )

        # 检查是否成功
        return response.status_code == 200

    except Exception as e:
        print(f"API 连接测试失败: {str(e)}")
        return False


def get_api_status() -> dict[str, str]:
    """
    获取 API 状态信息

    检查各个 API 的配置和连接状态。

    Returns:
        dict[str, str]: 状态信息字典

    Example:
        >>> status = get_api_status()
        >>> print(status)
        {
            'openrouter': '已配置',
            'replicate': '已配置',
            'connection': '正常'
        }
    """
    from config import OPENROUTER_API_KEY

    # 检查 OpenRouter 配置
    openrouter_status = "已配置" if OPENROUTER_API_KEY else "未配置"

    # 检查 Replicate 配置
    replicate_status = "已配置" if REPLICATE_API_TOKEN else "未配置"

    # 测试连接
    connection_ok = test_api_connection()
    connection_status = "正常" if connection_ok else "异常"

    return {
        "openrouter": openrouter_status,
        "replicate": replicate_status,
        "connection": connection_status
    }
