"""运行时配置兼容 API 路由。配置由浏览器保存，请求头负责下发。"""

from fastapi import APIRouter, HTTPException

from ...config import get_runtime_settings_status

router = APIRouter(prefix="/settings", tags=["运行时配置"])


@router.get("")
async def get_settings():
    """仅返回配置状态，不返回任何密钥。"""
    return {
        "success": True,
        "message": "配置仅保存在当前浏览器中，服务器不会保存",
        "data": get_runtime_settings_status(),
    }


@router.put("")
async def save_settings():
    """拒绝旧版后端持久化调用。"""
    raise HTTPException(
        status_code=410,
        detail="后端配置保存接口已停用，请使用前端设置页保存到当前浏览器",
    )
