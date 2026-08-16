"""配置管理模块"""

import base64
import binascii
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# 加载环境变量
# 首先尝试加载当前目录的.env
load_dotenv()

# 然后尝试加载HelloAgents的.env(如果存在)
helloagents_env = Path(__file__).parent.parent.parent.parent / "HelloAgents" / ".env"
if helloagents_env.exists():
    load_dotenv(helloagents_env, override=False)  # 不覆盖已有的环境变量


class Settings(BaseSettings):
    """应用配置"""

    # 应用基本配置
    app_name: str = "云程 AI 旅行助手"
    app_version: str = "2.0.0"
    debug: bool = False

    # 服务器配置
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS配置 - 使用字符串,在代码中分割
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000"

    # 高德地图API配置
    vite_amap_web_key: str = ""
    vite_amap_web_js_key: str = ""

    # Google Maps API配置
    google_maps_api_key: str = ""
    google_maps_proxy: str = ""

    # 小红书配置
    xhs_cookie: str = ""

    # LLM配置 (从环境变量读取,由HelloAgents管理)
    openai_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("OPENAI_API_KEY", "LLM_API_KEY"),
    )
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        validation_alias=AliasChoices("OPENAI_BASE_URL", "LLM_BASE_URL"),
    )
    openai_model: str = Field(
        default="gpt-4",
        validation_alias=AliasChoices("OPENAI_MODEL", "LLM_MODEL_ID"),
    )

    # 日志配置
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # 忽略额外的环境变量

    def get_cors_origins_list(self) -> List[str]:
        """获取CORS origins列表"""
        return [origin.strip() for origin in self.cors_origins.split(',')]


# 创建全局配置实例
settings = Settings()
_RUNTIME_SETTINGS_FILE = Path(__file__).resolve().parent.parent / "runtime_settings.json"
RUNTIME_SETTINGS_HEADER = "X-CloudWay-Runtime-Settings"
_MAX_RUNTIME_SETTINGS_HEADER_LENGTH = 16_384
_RUNTIME_SETTING_KEYS = {
    "vite_amap_web_key",
    "vite_amap_web_js_key",
    "google_maps_api_key",
    "google_maps_proxy",
    "xhs_cookie",
    "openai_api_key",
    "openai_base_url",
    "openai_model",
}
_BASE_RUNTIME_SETTINGS = {
    key: str(getattr(settings, key, "") or "")
    for key in _RUNTIME_SETTING_KEYS
}


def _remove_legacy_runtime_settings_file() -> None:
    """删除旧版本在服务器上持久化的敏感配置文件。"""
    try:
        _RUNTIME_SETTINGS_FILE.unlink(missing_ok=True)
    except Exception as e:
        print(f"⚠️  删除旧运行时配置文件失败: {e}")


def decode_client_runtime_settings(encoded: str) -> Dict[str, str]:
    """解码浏览器请求头中的运行配置，只返回允许的字段。"""
    if not encoded:
        return {}
    if len(encoded) > _MAX_RUNTIME_SETTINGS_HEADER_LENGTH:
        raise ValueError("浏览器配置过大，请精简 Cookie 或代理配置")

    try:
        raw = base64.b64decode(encoded, validate=True).decode("utf-8")
        payload = json.loads(raw)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
        raise ValueError("浏览器配置格式无效") from e

    if not isinstance(payload, dict):
        raise ValueError("浏览器配置必须是对象")

    decoded: Dict[str, str] = {}
    for key in _RUNTIME_SETTING_KEYS:
        if key not in payload:
            continue
        value = payload[key]
        if value is not None and not isinstance(value, str):
            raise ValueError(f"浏览器配置字段 {key} 格式无效")
        decoded[key] = str(value or "").strip()
    return decoded


_remove_legacy_runtime_settings_file()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings


def get_runtime_settings() -> Dict[str, str]:
    """获取当前运行时配置（供前端设置页读取）。"""
    return {
        "vite_amap_web_key": settings.vite_amap_web_key or "",
        "vite_amap_web_js_key": settings.vite_amap_web_js_key or "",
        "google_maps_api_key": settings.google_maps_api_key or "",
        "google_maps_proxy": settings.google_maps_proxy or "",
        "xhs_cookie": settings.xhs_cookie or "",
        "openai_api_key": settings.openai_api_key or "",
        "openai_base_url": settings.openai_base_url or "",
        "openai_model": settings.openai_model or "",
    }


def update_runtime_settings(updates: Dict[str, Any]) -> Dict[str, str]:
    """将浏览器配置应用到当前进程内存，不写入文件或环境变量。"""
    for key in _RUNTIME_SETTING_KEYS:
        client_value = str(updates.get(key) or "").strip()
        setattr(settings, key, client_value or _BASE_RUNTIME_SETTINGS[key])
    return get_runtime_settings()


def apply_client_runtime_settings(encoded: str) -> bool:
    """应用浏览器配置，请求内容变化时返回 True。"""
    updates = decode_client_runtime_settings(encoded)
    if not updates:
        return False

    before = get_runtime_settings()
    after = update_runtime_settings(updates)
    return before != after


def get_runtime_settings_status() -> Dict[str, bool | str]:
    """仅返回配置状态，避免通过接口泄露服务器或浏览器密钥。"""
    return {
        "storage": "browser",
        "llm_configured": bool(settings.openai_api_key),
        "amap_configured": bool(settings.vite_amap_web_key),
        "google_maps_configured": bool(settings.google_maps_api_key),
        "xhs_configured": bool(settings.xhs_cookie),
    }


# 验证必要的配置
def validate_config():
    """验证配置是否完整"""
    warnings = []

    if not settings.vite_amap_web_key:
        warnings.append("VITE_AMAP_WEB_KEY未配置，景点地理编码等功能将不可用")

    llm_api_key = settings.openai_api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not llm_api_key:
        warnings.append("LLM API Key未配置，AI 生成功能将不可用")

    if warnings:
        print("\n⚠️  配置警告:")
        for w in warnings:
            print(f"  - {w}")

    return True


# 打印配置信息(用于调试)
def print_config():
    """打印当前配置(隐藏敏感信息)"""
    print(f"应用名称: {settings.app_name}")
    print(f"版本: {settings.app_version}")
    print(f"服务器: {settings.host}:{settings.port}")
    print(f"高德地图API Key: {'已配置' if settings.vite_amap_web_key else '未配置'}")
    print(f"高德地图JS Key: {'已配置' if settings.vite_amap_web_js_key else '未配置'}")
    print(f"Google Maps API Key: {'已配置' if settings.google_maps_api_key else '未配置'}")
    print(f"Google Maps Proxy: {settings.google_maps_proxy or '未配置'}")
    print(f"小红书Cookie: {'已配置' if settings.xhs_cookie else '未配置'}")

    # 检查LLM配置
    llm_api_key = settings.openai_api_key or os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    llm_base_url = settings.openai_base_url
    llm_model = settings.openai_model

    print(f"LLM API Key: {'已配置' if llm_api_key else '未配置'}")
    print(f"LLM Base URL: {llm_base_url}")
    print(f"LLM Model: {llm_model}")
    print(f"日志级别: {settings.log_level}")

