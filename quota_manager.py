"""
MoodPaper - AI 情绪壁纸生成应用
文件名: quota_manager.py
功能: 免费用户配额管理
作者: MoodPaper 团队
创建日期: 2025-10-24

主要功能:
1. 每日生成配额管理（标清3次/天，超清1次/天）
2. 超清下载配额管理（1次/天）
3. 每日自动重置
"""

import json
import os
from datetime import datetime
from typing import Dict, Tuple
from config import CACHE_DIR


# 配额数据文件
QUOTA_FILE = os.path.join(CACHE_DIR, "quota.json")

# 免费用户每日配额
FREE_USER_QUOTA = {
    "standard_generate": 2,    # 标清生成次数（每次生成1张，共2次机会）
    "hd_upgrade": 1            # 超清升级次数（选择喜欢的图升级为超清）
}


def ensure_quota_file() -> None:
    """
    确保配额文件存在
    """
    if not os.path.exists(QUOTA_FILE):
        reset_quota()


def load_quota() -> Dict:
    """
    加载配额数据

    Returns:
        Dict: 配额数据
    """
    ensure_quota_file()

    try:
        with open(QUOTA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # 检查日期，如果是新的一天，重置配额
            last_date = data.get("date")
            today = datetime.now().strftime("%Y-%m-%d")

            if last_date != today:
                # 新的一天，重置配额
                return reset_quota()

            return data
    except Exception as e:
        print(f"⚠️ 加载配额数据失败: {str(e)}")
        return reset_quota()


def save_quota(quota_data: Dict) -> bool:
    """
    保存配额数据

    Args:
        quota_data: 配额数据

    Returns:
        bool: 是否保存成功
    """
    try:
        with open(QUOTA_FILE, 'w', encoding='utf-8') as f:
            json.dump(quota_data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ 保存配额数据失败: {str(e)}")
        return False


def reset_quota() -> Dict:
    """
    重置配额为当日初始值

    Returns:
        Dict: 重置后的配额数据
    """
    today = datetime.now().strftime("%Y-%m-%d")

    quota_data = {
        "date": today,
        "standard_generate_used": 0,
        "hd_upgrade_used": 0,
        "standard_generate_limit": FREE_USER_QUOTA["standard_generate"],
        "hd_upgrade_limit": FREE_USER_QUOTA["hd_upgrade"]
    }

    save_quota(quota_data)
    return quota_data


def check_quota(quota_type: str) -> Tuple[bool, str, int, int]:
    """
    检查配额是否还有剩余

    Args:
        quota_type: 配额类型 ("standard_generate", "hd_upgrade")

    Returns:
        Tuple[bool, str, int, int]: (是否有剩余, 提示信息, 已使用, 总限制)
    """
    quota_data = load_quota()

    used_key = f"{quota_type}_used"
    limit_key = f"{quota_type}_limit"

    used = quota_data.get(used_key, 0)
    limit = quota_data.get(limit_key, 0)
    remaining = limit - used

    if remaining > 0:
        return True, f"剩余 {remaining} 次", used, limit
    else:
        return False, "今日配额已用完", used, limit


def use_quota(quota_type: str) -> Tuple[bool, str]:
    """
    使用一次配额

    Args:
        quota_type: 配额类型

    Returns:
        Tuple[bool, str]: (是否成功, 提示信息)
    """
    quota_data = load_quota()

    used_key = f"{quota_type}_used"
    limit_key = f"{quota_type}_limit"

    used = quota_data.get(used_key, 0)
    limit = quota_data.get(limit_key, 0)

    if used < limit:
        quota_data[used_key] = used + 1
        if save_quota(quota_data):
            remaining = limit - used - 1
            return True, f"使用成功，今日还剩 {remaining} 次"
        else:
            return False, "保存配额失败"
    else:
        return False, f"今日配额已用完，明天再来吧！"


def get_quota_status() -> Dict:
    """
    获取所有配额状态

    Returns:
        Dict: 配额状态信息
    """
    quota_data = load_quota()

    return {
        "standard_generate": {
            "used": quota_data.get("standard_generate_used", 0),
            "limit": quota_data.get("standard_generate_limit", 0),
            "remaining": quota_data.get("standard_generate_limit", 0) - quota_data.get("standard_generate_used", 0)
        },
        "hd_upgrade": {
            "used": quota_data.get("hd_upgrade_used", 0),
            "limit": quota_data.get("hd_upgrade_limit", 0),
            "remaining": quota_data.get("hd_upgrade_limit", 0) - quota_data.get("hd_upgrade_used", 0)
        },
        "date": quota_data.get("date", "")
    }


def get_quota_summary() -> str:
    """
    获取配额摘要（用于UI显示）

    Returns:
        str: 配额摘要文本
    """
    status = get_quota_status()

    summary = f"""
📊 **今日配额使用情况**

- 📷 标清生成：{status['standard_generate']['used']}/{status['standard_generate']['limit']} (剩余 {status['standard_generate']['remaining']} 次)
- ⭐ 超清升级：{status['hd_upgrade']['used']}/{status['hd_upgrade']['limit']} (剩余 {status['hd_upgrade']['remaining']} 次)

💡 提示：看到喜欢的壁纸后，点击"升级超清"按钮获得2K高清版本
    """

    return summary.strip()
