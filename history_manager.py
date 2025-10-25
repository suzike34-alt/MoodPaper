"""
MoodPaper - AI 情绪壁纸生成应用
文件名: history_manager.py
功能: 历史记录和收藏管理
作者: MoodPaper 团队
创建日期: 2025-10-24

主要功能:
1. 保存生成的壁纸到历史记录
2. 加载历史记录
3. 管理收藏功能
4. 删除历史记录
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from PIL import Image
from config import CACHE_DIR


# 历史记录文件路径
HISTORY_FILE = os.path.join(CACHE_DIR, "history.json")


def ensure_history_file() -> None:
    """
    确保历史记录文件存在
    """
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({"history": []}, f, ensure_ascii=False, indent=2)


def load_history() -> List[Dict]:
    """
    加载历史记录

    Returns:
        List[Dict]: 历史记录列表
    """
    ensure_history_file()

    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("history", [])
    except Exception as e:
        print(f"⚠️ 加载历史记录失败: {str(e)}")
        return []


def save_history(history: List[Dict]) -> bool:
    """
    保存历史记录

    Args:
        history: 历史记录列表

    Returns:
        bool: 是否保存成功
    """
    ensure_history_file()

    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump({"history": history}, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存历史记录失败: {str(e)}")
        return False


def add_to_history(
    mood: str,
    style: str,
    quote: str,
    original_img,
    landscape_img=None,
    portrait_img=None,
    aspect_ratio: str = "9:16"
) -> Optional[Dict]:
    """
    添加新记录到历史

    Args:
        mood: 心情关键词
        style: 风格
        quote: 签文
        original_img: 原图（可以是 PIL Image 对象或文件路径字符串）
        landscape_img: 横屏图（可选，PIL Image 对象或文件路径字符串）
        portrait_img: 竖屏图（可选，PIL Image 对象或文件路径字符串）
        aspect_ratio: 图片比例 (默认 "9:16")

    Returns:
        Optional[Dict]: 添加的记录，失败返回 None
    """
    try:
        # 生成唯一 ID
        timestamp = datetime.now()
        record_id = timestamp.strftime("%Y%m%d_%H%M%S")

        # 处理原图
        if isinstance(original_img, str):
            # 如果是文件路径，直接使用
            original_path = original_img
        else:
            # 如果是 PIL Image，保存
            original_path = os.path.join(CACHE_DIR, f"{record_id}_original.png")
            original_img.save(original_path, "PNG")

        # 处理横屏图（可选）
        if landscape_img:
            if isinstance(landscape_img, str):
                landscape_path = landscape_img
            else:
                landscape_path = os.path.join(CACHE_DIR, f"{record_id}_landscape.png")
                landscape_img.save(landscape_path, "PNG")
        else:
            landscape_path = None

        # 处理竖屏图（可选）
        if portrait_img:
            if isinstance(portrait_img, str):
                portrait_path = portrait_img
            else:
                portrait_path = os.path.join(CACHE_DIR, f"{record_id}_portrait.png")
                portrait_img.save(portrait_path, "PNG")
        else:
            portrait_path = None

        # 创建记录
        record = {
            "id": record_id,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "mood": mood,
            "style": style,
            "quote": quote,
            "aspect_ratio": aspect_ratio,  # 图片比例
            "original_path": original_path,
            "landscape_path": landscape_path,
            "portrait_path": portrait_path,
            "hd_path": None,  # HD 版本路径（初始为空）
            "is_favorite": False
        }

        # 加载现有历史
        history = load_history()

        # 添加新记录到开头（最新的在最前面）
        history.insert(0, record)

        # 限制历史记录数量（最多保存 100 条）
        if len(history) > 100:
            # 删除最旧的记录及其图片文件
            old_record = history.pop()
            for path_key in ['original_path', 'landscape_path', 'portrait_path', 'hd_path']:
                path = old_record.get(path_key)
                if path and os.path.exists(path):
                    os.remove(path)

        # 保存历史
        if save_history(history):
            return record
        else:
            return None

    except Exception as e:
        print(f"❌ 添加历史记录失败: {str(e)}")
        return None


def update_hd_path(record_id: str, hd_path: str) -> bool:
    """
    更新记录的 HD 版本路径

    Args:
        record_id: 记录 ID
        hd_path: HD 图片路径

    Returns:
        bool: 是否更新成功
    """
    history = load_history()

    for record in history:
        if record["id"] == record_id:
            record["hd_path"] = hd_path
            return save_history(history)

    return False


def get_all_history() -> List[Dict]:
    """
    获取所有历史记录（别名函数，为了 API 兼容性）

    Returns:
        List[Dict]: 历史记录列表
    """
    return load_history()


def toggle_favorite(record_id: str) -> bool:
    """
    切换收藏状态

    Args:
        record_id: 记录 ID

    Returns:
        bool: 是否操作成功
    """
    history = load_history()

    for record in history:
        if record["id"] == record_id:
            record["is_favorite"] = not record["is_favorite"]
            return save_history(history)

    return False


def get_favorites() -> List[Dict]:
    """
    获取所有收藏的记录

    Returns:
        List[Dict]: 收藏列表
    """
    history = load_history()
    return [record for record in history if record.get("is_favorite", False)]


def delete_record(record_id: str) -> bool:
    """
    删除历史记录

    Args:
        record_id: 记录 ID

    Returns:
        bool: 是否删除成功
    """
    history = load_history()

    for i, record in enumerate(history):
        if record["id"] == record_id:
            # 删除图片文件（包括 HD 版本）
            for path_key in ['original_path', 'landscape_path', 'portrait_path', 'hd_path']:
                path = record.get(path_key)
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as e:
                        print(f"⚠️ 删除文件失败 {path}: {str(e)}")

            # 从历史中删除
            history.pop(i)
            return save_history(history)

    return False


def get_record_by_id(record_id: str) -> Optional[Dict]:
    """
    根据 ID 获取记录

    Args:
        record_id: 记录 ID

    Returns:
        Optional[Dict]: 记录详情，不存在返回 None
    """
    history = load_history()

    for record in history:
        if record["id"] == record_id:
            return record

    return None
