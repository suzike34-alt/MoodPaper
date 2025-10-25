"""
MoodPaper - AI 情绪壁纸生成应用
文件名: membership.py
功能: 会员管理系统
作者: MoodPaper 团队
创建日期: 2025-10-24

主要功能:
1. 会员状态验证
2. 会员码管理
3. 图片质量等级控制
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from config import CACHE_DIR


# 会员数据文件
MEMBERSHIP_FILE = os.path.join(CACHE_DIR, "membership.json")

# 预设的会员码（演示用）
VALID_MEMBERSHIP_CODES = {
    "VIPUSER2024": {"duration_days": 365, "level": "premium"},
    "TRIAL2024": {"duration_days": 7, "level": "trial"},
    "FOREVER": {"duration_days": 9999, "level": "premium"}  # 永久会员
}


def ensure_membership_file() -> None:
    """
    确保会员数据文件存在
    """
    if not os.path.exists(MEMBERSHIP_FILE):
        with open(MEMBERSHIP_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "is_member": False,
                "member_level": "free",
                "expiry_date": None,
                "activation_date": None
            }, f, ensure_ascii=False, indent=2)


def load_membership() -> Dict:
    """
    加载会员信息

    Returns:
        Dict: 会员信息字典
    """
    ensure_membership_file()

    try:
        with open(MEMBERSHIP_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ 加载会员信息失败: {str(e)}")
        return {
            "is_member": False,
            "member_level": "free",
            "expiry_date": None,
            "activation_date": None
        }


def save_membership(membership_data: Dict) -> bool:
    """
    保存会员信息

    Args:
        membership_data: 会员信息字典

    Returns:
        bool: 是否保存成功
    """
    ensure_membership_file()

    try:
        with open(MEMBERSHIP_FILE, 'w', encoding='utf-8') as f:
            json.dump(membership_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存会员信息失败: {str(e)}")
        return False


def activate_membership(code: str) -> tuple[bool, str]:
    """
    激活会员

    Args:
        code: 会员激活码

    Returns:
        tuple[bool, str]: (是否成功, 提示消息)
    """
    # 验证激活码
    if code not in VALID_MEMBERSHIP_CODES:
        return False, "❌ 无效的会员码"

    code_info = VALID_MEMBERSHIP_CODES[code]

    # 计算到期时间
    activation_date = datetime.now()
    expiry_date = activation_date + timedelta(days=code_info["duration_days"])

    # 保存会员信息
    membership_data = {
        "is_member": True,
        "member_level": code_info["level"],
        "expiry_date": expiry_date.strftime("%Y-%m-%d %H:%M:%S"),
        "activation_date": activation_date.strftime("%Y-%m-%d %H:%M:%S")
    }

    if save_membership(membership_data):
        duration_days = code_info["duration_days"]
        if duration_days > 365:
            return True, f"✅ 会员激活成功！您已获得永久会员资格"
        else:
            return True, f"✅ 会员激活成功！有效期至 {expiry_date.strftime('%Y-%m-%d')}"
    else:
        return False, "❌ 激活失败，请稍后重试"


def check_membership_status() -> Dict:
    """
    检查会员状态

    Returns:
        Dict: 会员状态信息
    """
    membership_data = load_membership()

    # 如果不是会员，直接返回
    if not membership_data.get("is_member", False):
        return {
            "is_active": False,
            "level": "free",
            "message": "免费用户"
        }

    # 检查是否过期
    expiry_str = membership_data.get("expiry_date")
    if expiry_str:
        try:
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d %H:%M:%S")
            now = datetime.now()

            if now > expiry_date:
                # 已过期，更新状态
                membership_data["is_member"] = False
                save_membership(membership_data)
                return {
                    "is_active": False,
                    "level": "free",
                    "message": "会员已过期"
                }
            else:
                # 未过期
                days_left = (expiry_date - now).days
                return {
                    "is_active": True,
                    "level": membership_data.get("member_level", "premium"),
                    "expiry_date": expiry_str,
                    "days_left": days_left,
                    "message": f"会员有效，剩余 {days_left} 天"
                }
        except Exception as e:
            print(f"⚠️ 解析会员到期时间失败: {str(e)}")
            return {
                "is_active": False,
                "level": "free",
                "message": "会员信息异常"
            }

    return {
        "is_active": False,
        "level": "free",
        "message": "免费用户"
    }


def get_image_quality_config(is_member: bool = False) -> Dict:
    """
    获取图片质量配置

    Args:
        is_member: 是否为会员

    Returns:
        Dict: 图片质量配置
    """
    if is_member:
        # 会员：超清配置
        return {
            "resolution": 2048,      # 2K分辨率
            "quality": 95,           # 高质量压缩
            "format": "PNG",         # PNG格式
            "steps": 80,             # 更多推理步数
            "label": "超清 (2K)",
            "size_estimate": "3-5 MB"
        }
    else:
        # 普通用户：标准配置
        return {
            "resolution": 1024,      # 1K分辨率
            "quality": 85,           # 标准压缩
            "format": "PNG",         # PNG格式
            "steps": 50,             # 标准推理步数
            "label": "标清 (1K)",
            "size_estimate": "300-800 KB"
        }


def is_member_active() -> bool:
    """
    检查会员是否激活（简化版）

    Returns:
        bool: 会员是否有效
    """
    status = check_membership_status()
    return status.get("is_active", False)


def get_membership_info() -> Dict:
    """
    获取会员信息（别名函数）

    Returns:
        Dict: 会员状态信息
    """
    return check_membership_status()


def cancel_membership() -> bool:
    """
    取消会员资格

    Returns:
        bool: 是否成功
    """
    membership_data = {
        "is_member": False,
        "member_level": "free",
        "expiry_date": None,
        "activation_date": None
    }
    return save_membership(membership_data)
