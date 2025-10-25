"""
MoodPaper - AI 情绪壁纸生成应用
文件名: image_processing.py
功能: 图片处理工具（裁剪、文字叠加）
作者: MoodPaper 团队
创建日期: 2025-10-24

主要功能:
1. 图片裁剪（原图、16:9、9:16）
2. 文字叠加（底部居中艺术字体）
3. 智能字体选择
"""

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import Optional, Tuple, List
import os


def crop_to_ratio(image: Image.Image, ratio: str) -> Image.Image:
    """
    将图片裁剪为指定比例

    Args:
        image: PIL Image 对象
        ratio: 比例类型 ("original", "16:9", "9:16")

    Returns:
        Image.Image: 裁剪后的图片
    """
    width, height = image.size

    if ratio == "original":
        return image

    elif ratio == "16:9":
        # 横屏 16:9
        target_ratio = 16 / 9
        current_ratio = width / height

        if current_ratio > target_ratio:
            # 宽度过大，裁剪左右
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            cropped = image.crop((left, 0, left + new_width, height))
        else:
            # 高度过大，裁剪上下
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            cropped = image.crop((0, top, width, top + new_height))

        return cropped

    elif ratio == "9:16":
        # 竖屏 9:16
        target_ratio = 9 / 16
        current_ratio = width / height

        if current_ratio > target_ratio:
            # 宽度过大，裁剪左右
            new_width = int(height * target_ratio)
            left = (width - new_width) // 2
            cropped = image.crop((left, 0, left + new_width, height))
        else:
            # 高度过大，裁剪上下
            new_height = int(width / target_ratio)
            top = (height - new_height) // 2
            cropped = image.crop((0, top, width, top + new_height))

        return cropped

    else:
        return image


def get_font(size: int) -> ImageFont.FreeTypeFont:
    """
    获取字体对象，优先使用系统中的艺术字体

    Args:
        size: 字体大小

    Returns:
        ImageFont.FreeTypeFont: 字体对象
    """
    # macOS 系统字体路径
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",  # 苹方字体（优雅）
        "/System/Library/Fonts/Supplemental/Songti.ttc",  # 宋体（古典）
        "/System/Library/Fonts/Supplemental/Kaiti.ttc",  # 楷体（艺术）
        "/System/Library/Fonts/Supplemental/STHeiti Medium.ttc",  # 黑体
        "/Library/Fonts/Arial Unicode.ttf",  # Arial Unicode
    ]

    # Windows 系统字体路径
    windows_fonts = [
        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simkai.ttf",  # 楷体
    ]

    font_paths.extend(windows_fonts)

    # 尝试加载字体
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    # 如果都失败，使用默认字体
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        # 最后使用 PIL 默认字体
        return ImageFont.load_default()


def add_text_with_outline(
    draw: ImageDraw.Draw,
    position: Tuple[int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    text_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    outline_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
    outline_width: int = 3
) -> None:
    """
    绘制带描边的文字

    Args:
        draw: ImageDraw 对象
        position: 文字位置 (x, y)
        text: 文字内容
        font: 字体对象
        text_color: 文字颜色
        outline_color: 描边颜色
        outline_width: 描边宽度
    """
    x, y = position

    # 绘制描边（多次绘制黑色文字形成描边效果）
    for adj_x in range(-outline_width, outline_width + 1):
        for adj_y in range(-outline_width, outline_width + 1):
            if adj_x != 0 or adj_y != 0:
                draw.text(
                    (x + adj_x, y + adj_y),
                    text,
                    font=font,
                    fill=outline_color
                )

    # 绘制主文字
    draw.text(position, text, font=font, fill=text_color)


def wrap_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: int,
    draw: ImageDraw.Draw
) -> List[str]:
    """
    自动换行文字

    Args:
        text: 要换行的文字
        font: 字体对象
        max_width: 最大宽度
        draw: ImageDraw 对象

    Returns:
        list: 换行后的文字列表
    """
    lines = []
    current_line = ""

    for char in text:
        test_line = current_line + char
        try:
            bbox = draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
        except AttributeError:
            test_width, _ = draw.textsize(test_line, font=font)

        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char

    if current_line:
        lines.append(current_line)

    return lines if lines else [text]


def add_text_to_image(
    image: Image.Image,
    text: str,
    position: str = "bottom",
    font_size: Optional[int] = None
) -> Image.Image:
    """
    在图片上添加文字水印（优化版，使用描边效果）

    Args:
        image: PIL Image 对象
        text: 要添加的文字
        position: 文字位置 ("bottom", "top", "center")
        font_size: 字体大小（自动根据图片大小调整）

    Returns:
        Image.Image: 添加文字后的图片
    """
    # 创建副本，避免修改原图
    img_copy = image.copy()

    # 转换为 RGBA 模式以支持透明度
    if img_copy.mode != 'RGBA':
        img_copy = img_copy.convert('RGBA')

    # 创建文字层
    txt_layer = Image.new('RGBA', img_copy.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    width, height = img_copy.size

    # 自动调整字体大小
    if font_size is None:
        # 根据图片大小和宽高比智能调整
        if width < height:  # 竖屏
            font_size = max(24, width // 15)
        else:  # 横屏或正方形
            font_size = max(30, min(width, height) // 18)

    # 获取字体
    font = get_font(font_size)

    # 检查文字是否需要换行（主要针对竖屏）
    max_text_width = int(width * 0.9)  # 留10%边距

    # 尝试获取单行文字宽度
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        single_line_height = bbox[3] - bbox[1]
    except AttributeError:
        text_width, single_line_height = draw.textsize(text, font=font)

    # 如果文字过长，进行换行或缩小字体
    if text_width > max_text_width:
        # 对于竖屏，优先换行
        if width < height:
            lines = wrap_text(text, font, max_text_width, draw)
        else:
            # 对于横屏，尝试缩小字体
            font_size = int(font_size * max_text_width / text_width * 0.95)
            font = get_font(font_size)
            lines = [text]
    else:
        lines = [text]

    # 计算总高度
    line_height = int(single_line_height * 1.2)  # 行间距
    total_height = len(lines) * line_height

    # 计算起始 Y 位置
    if position == "bottom":
        # 底部，留出边距
        y_start = height - total_height - int(height * 0.05)
    elif position == "top":
        # 顶部，留出边距
        y_start = int(height * 0.05)
    else:
        # 居中
        y_start = (height - total_height) // 2

    # 绘制每一行文字
    for i, line in enumerate(lines):
        # 计算当前行的宽度
        try:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
        except AttributeError:
            line_width, _ = draw.textsize(line, font=font)

        # 居中对齐
        x = (width - line_width) // 2
        y = y_start + i * line_height

        # 绘制带描边的文字
        add_text_with_outline(
            draw=draw,
            position=(x, y),
            text=line,
            font=font,
            text_color=(255, 255, 255, 255),  # 白色文字
            outline_color=(0, 0, 0, 200),     # 黑色描边
            outline_width=max(2, font_size // 15)  # 根据字体大小调整描边宽度
        )

    # 合并文字层和原图
    img_copy = Image.alpha_composite(img_copy, txt_layer)

    # 转回 RGB 模式
    rgb_img = Image.new('RGB', img_copy.size, (255, 255, 255))
    rgb_img.paste(img_copy, mask=img_copy.split()[3])

    return rgb_img


def process_wallpaper(
    image_path: str,
    ratio: str = "original",
    add_text: bool = False,
    text: str = ""
) -> Image.Image:
    """
    处理壁纸：裁剪（可选添加文字）

    Args:
        image_path: 图片路径（URL 或本地路径）
        ratio: 裁剪比例 ("original", "16:9", "9:16")
        add_text: 是否添加文字（默认 False）
        text: 要添加的签文（仅当 add_text=True 时使用）

    Returns:
        Image.Image: 处理后的图片
    """
    # 打开图片
    if image_path.startswith(('http://', 'https://')):
        import requests
        response = requests.get(image_path, timeout=30)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(image_path)

    # 裁剪
    cropped = crop_to_ratio(img, ratio)

    # 可选：添加文字
    if add_text and text:
        return add_text_to_image(cropped, text, position="bottom")
    else:
        return cropped


def image_to_bytes(image: Image.Image, format: str = "PNG", quality: int = 95) -> bytes:
    """
    将 PIL Image 转换为字节流

    Args:
        image: PIL Image 对象
        format: 图片格式
        quality: 图片质量（1-100，仅对JPEG有效）

    Returns:
        bytes: 图片字节数据
    """
    buf = BytesIO()
    if format.upper() == "JPEG":
        image.save(buf, format=format, quality=quality, optimize=True)
    else:
        # PNG格式，使用compress_level控制压缩
        # compress_level: 0-9, 0=无压缩, 9=最大压缩
        compress_level = 9 - (quality // 11)  # 将质量转换为压缩级别
        image.save(buf, format=format, compress_level=max(0, min(9, compress_level)))
    return buf.getvalue()
