"""
MoodPaper - AI 情绪壁纸生成应用
文件名: backend/main.py
功能: FastAPI 后端服务
作者: MoodPaper 团队
创建日期: 2025-10-24

主要功能:
1. 壁纸生成 API
2. 超清升级 API
3. 配额管理 API
4. 历史记录 API
5. 会员管理 API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import sys
import os
import time
import hashlib

# 添加父目录到路径，以便导入现有模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import generate_wallpaper, generate_quote
from quota_manager import (
    check_quota,
    use_quota,
    get_quota_status,
    get_quota_summary
)
from history_manager import (
    add_to_history,
    get_all_history,
    toggle_favorite,
    get_favorites,
    delete_record,
    update_hd_path
)
from membership import (
    is_member_active,
    activate_membership,
    get_membership_info,
    get_image_quality_config
)
from image_processing import (
    process_wallpaper,
    image_to_bytes
)
from prompts import STYLE_PROMPTS

# 调试模式：设置为 True 时禁用配额限制
DEBUG_MODE = True  # 🔧 调试时设为 True，生产环境改为 False

# 创建 FastAPI 应用
app = FastAPI(
    title="MoodPaper API",
    description="AI 情绪壁纸生成服务",
    version="1.0.0"
)

# 配置 CORS（允许 React 前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite 默认端口
        "http://localhost:3000",  # Create React App 默认端口
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== Pydantic 模型 ====================

class GenerateRequest(BaseModel):
    mood: str
    style: str
    aspect_ratio: Optional[str] = "9:16"  # 默认 9:16 竖向宽屏

class UpgradeRequest(BaseModel):
    image_path: str
    record_id: Optional[str] = None

class MembershipActivateRequest(BaseModel):
    code: str

class FavoriteToggleRequest(BaseModel):
    record_id: str


# ==================== API 端点 ====================

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "MoodPaper API Server",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/api/styles")
async def get_styles():
    """获取所有可用的风格列表"""
    styles = []
    for style_key, style_data in STYLE_PROMPTS.items():
        styles.append({
            "key": style_key,
            "name": style_data["name"],
            "description": style_data.get("description", "")
        })
    return {"styles": styles}


@app.get("/api/quota")
async def get_quota():
    """获取当前配额状态"""
    try:
        status = get_quota_status()
        summary = get_quota_summary()
        return {
            "status": status,
            "summary": summary,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配额失败: {str(e)}")


@app.post("/api/generate")
async def generate(request: GenerateRequest):
    """
    生成标清壁纸

    流程:
    1. 检查配额
    2. 生成签文
    3. 生成壁纸
    4. 保存历史记录
    5. 扣除配额
    """
    try:
        # 1. 检查配额（调试模式下跳过）
        if DEBUG_MODE:
            print("🔧 调试模式：跳过配额检查")
            has_quota = True
            used, limit = 0, 2
            quota_msg = "调试模式：无限制"
        else:
            has_quota, message, used, limit = check_quota("standard_generate")
            if not has_quota:
                raise HTTPException(status_code=403, detail=message)

        # 2. 生成签文
        quote = generate_quote(request.mood)

        # 3. 生成壁纸（根据比例选择分辨率）
        # 通义万相支持: 1:1 (1024*1024), 16:9 (1280*720), 9:16 (720*1280)
        image_path = generate_wallpaper(
            mood_keyword=request.mood,
            selected_style=request.style,
            aspect_ratio=request.aspect_ratio or "9:16"
        )

        if not image_path:
            raise HTTPException(status_code=500, detail="壁纸生成失败")

        # 4. 保存到历史记录
        record = add_to_history(
            mood=request.mood,
            style=request.style,
            quote=quote,
            original_img=image_path,
            landscape_img=None,
            portrait_img=None,
            aspect_ratio=request.aspect_ratio or "9:16"
        )

        # 5. 扣除配额（调试模式下跳过）
        if not DEBUG_MODE:
            success, quota_msg = use_quota("standard_generate")
            if not success:
                print(f"⚠️ 配额扣除失败: {quota_msg}")
        else:
            quota_msg = "调试模式：无限制"

        # 6. 返回结果
        return {
            "success": True,
            "image_path": image_path,
            "quote": quote,
            "record_id": record["id"] if record else None,
            "quota_message": quota_msg,
            "quota_remaining": limit - used - 1 if not DEBUG_MODE else 999
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@app.post("/api/upgrade")
async def upgrade_to_hd(request: UpgradeRequest):
    """
    升级到超清壁纸 (2048x2048)

    流程:
    1. 检查超清升级配额
    2. 生成 2K 壁纸
    3. 更新历史记录（如果有 record_id）
    4. 扣除升级配额
    """
    try:
        # 1. 检查配额（调试模式下跳过）
        if DEBUG_MODE:
            print("🔧 调试模式：跳过配额检查")
            has_quota = True
            used, limit = 0, 1
            quota_msg = "调试模式：无限制"
        else:
            has_quota, message, used, limit = check_quota("hd_upgrade")
            if not has_quota:
                raise HTTPException(status_code=403, detail=message)

        # 2. 从历史记录获取原始信息
        all_history = get_all_history()
        record = None
        if request.record_id:
            for r in all_history:
                if r["id"] == request.record_id:
                    record = r
                    break

        if not record:
            raise HTTPException(status_code=404, detail="找不到原始记录")

        # 3. 生成超清壁纸
        # 获取原始比例，如果没有记录则默认使用 1:1
        original_aspect_ratio = record.get("aspect_ratio", "1:1")

        # 对于 1:1 比例，使用通义万相生成 2048*2048 超清图
        # 对于 16:9 和 9:16，通义万相没有更高分辨率，使用 PIL 放大原图
        if original_aspect_ratio == "1:1":
            # 使用通义万相生成 2048*2048 超清图
            hd_image_path = generate_wallpaper(
                mood_keyword=record["mood"],
                selected_style=record["style"],
                aspect_ratio=original_aspect_ratio,
                is_hd=True
            )
        else:
            # 对于 16:9 和 9:16，放大原图到 2 倍分辨率
            from PIL import Image

            # 获取原图路径
            original_path = record.get("original_path")
            if not original_path or not os.path.exists(original_path):
                raise HTTPException(status_code=404, detail="原始图片不存在")

            # 打开原图
            img = Image.open(original_path)
            original_size = img.size

            # 放大到 2 倍
            new_size = (original_size[0] * 2, original_size[1] * 2)
            img_hd = img.resize(new_size, Image.Resampling.LANCZOS)

            # 保存超清版本
            timestamp = int(time.time())
            hash_str = hashlib.md5(record["mood"].encode()).hexdigest()[:8]
            hd_filename = f"hd_{timestamp}_{hash_str}.png"

            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            hd_image_path = os.path.join(project_root, "output", hd_filename)

            img_hd.save(hd_image_path, "PNG", quality=95)
            print(f"✅ 图片已放大至 {new_size[0]}x{new_size[1]}: {hd_image_path}")

        if not hd_image_path:
            raise HTTPException(status_code=500, detail="超清壁纸生成失败")

        # 4. 更新历史记录（添加 HD 版本）
        if request.record_id:
            update_hd_path(request.record_id, hd_image_path)

        # 5. 扣除配额（调试模式下跳过）
        if not DEBUG_MODE:
            success, quota_msg = use_quota("hd_upgrade")
            if not success:
                print(f"⚠️ 配额扣除失败: {quota_msg}")
        else:
            quota_msg = "调试模式：无限制"

        return {
            "success": True,
            "hd_image_path": hd_image_path,
            "quota_message": quota_msg,
            "quota_remaining": limit - used - 1 if not DEBUG_MODE else 999
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"升级失败: {str(e)}")


@app.get("/api/history")
async def get_history():
    """获取所有历史记录"""
    try:
        history = get_all_history()
        return {
            "success": True,
            "history": history,
            "total": len(history)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史失败: {str(e)}")


@app.get("/api/favorites")
async def get_favorite_list():
    """获取收藏列表"""
    try:
        favorites = get_favorites()
        return {
            "success": True,
            "favorites": favorites,
            "total": len(favorites)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏失败: {str(e)}")


@app.post("/api/favorite/toggle")
async def toggle_favorite_status(request: FavoriteToggleRequest):
    """切换收藏状态"""
    try:
        success = toggle_favorite(request.record_id)
        if success:
            return {
                "success": True,
                "message": "收藏状态已切换"
            }
        else:
            raise HTTPException(status_code=404, detail="记录不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"切换收藏失败: {str(e)}")


@app.delete("/api/history/{record_id}")
async def delete_history_record(record_id: str):
    """删除历史记录"""
    try:
        success = delete_record(record_id)
        if success:
            return {
                "success": True,
                "message": "记录已删除"
            }
        else:
            raise HTTPException(status_code=404, detail="记录不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@app.get("/api/membership")
async def get_membership_status():
    """获取会员状态"""
    try:
        is_active = is_member_active()
        info = get_membership_info()
        quality_config = get_image_quality_config(is_active)

        return {
            "success": True,
            "is_active": is_active,
            "info": info,
            "quality_config": quality_config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会员信息失败: {str(e)}")


@app.post("/api/membership/activate")
async def activate_member(request: MembershipActivateRequest):
    """激活会员"""
    try:
        success, message = activate_membership(request.code)
        if success:
            return {
                "success": True,
                "message": message
            }
        else:
            raise HTTPException(status_code=400, detail=message)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"激活失败: {str(e)}")


@app.get("/api/image/{filename}")
async def get_image(filename: str):
    """获取图片文件（用于前端显示）"""
    try:
        # 使用绝对路径查找图片
        # 项目根目录在 backend 的上一级
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, "output", filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"图片不存在: {filename}")

        return FileResponse(file_path, media_type="image/png")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图片失败: {str(e)}")


@app.get("/api/download/{filename}")
async def download_image(filename: str, ratio: Optional[str] = "original"):
    """
    下载图片（支持裁剪）

    Args:
        filename: 图片文件名
        ratio: 裁剪比例 (original, 16:9, 9:16)
    """
    try:
        # 使用绝对路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(project_root, "output", filename)

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"图片不存在: {filename}")

        # 如果需要裁剪
        if ratio and ratio != "original":
            from PIL import Image
            processed_img = process_wallpaper(
                image_path=file_path,
                ratio=ratio,
                add_text=False
            )

            # 转换为字节流
            img_bytes = image_to_bytes(processed_img, format="PNG", quality=95)

            # 生成新文件名
            base_name = os.path.splitext(filename)[0]
            new_filename = f"{base_name}_{ratio.replace(':', '-')}.png"

            return JSONResponse(
                content={
                    "success": True,
                    "data": img_bytes.decode('latin1'),  # 二进制数据
                    "filename": new_filename
                }
            )
        else:
            # 直接返回原图
            return FileResponse(
                file_path,
                media_type="image/png",
                filename=filename
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


# ==================== 健康检查 ====================

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "MoodPaper API",
        "version": "1.0.0"
    }


# ==================== 运行服务器 ====================

if __name__ == "__main__":
    import uvicorn

    print("🚀 MoodPaper API 服务器启动中...")
    print("📍 访问地址: http://localhost:8000")
    print("📚 API 文档: http://localhost:8000/docs")
    print("🔄 交互式文档: http://localhost:8000/redoc")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下自动重载
        log_level="info"
    )
