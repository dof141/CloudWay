# Browser-Owned Runtime Settings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将用户填写的第三方密钥只保存在浏览器中，并让后端在不持久化密钥的前提下使用这些配置。

**Architecture:** 前端使用 `localStorage` 保存完整运行配置，Axios 拦截器通过 `X-CloudWay-Runtime-Settings` 请求头发送 Base64 编码的 JSON。后端中间件解析并应用到单用户进程内存，配置变化时重置相关服务单例；旅行请求体和任务持久化结构保持不变。

**Tech Stack:** Vue 3、TypeScript、Axios、Vue I18n、FastAPI、Pydantic

---

### Task 1: 浏览器配置存储与请求传递

**Files:**
- Modify: `frontend/src/services/api.ts`
- Modify: `frontend/src/types/index.ts`

- [ ] 将后端运行配置序列化到版本化 `localStorage` Key，读取失败时回退空配置。
- [ ] 将 `getRuntimeSettings` 和 `saveRuntimeSettings` 改为纯浏览器操作，不再调用 `/api/settings`。
- [ ] 增加 `clearRuntimeSettings`，删除所有运行配置相关的浏览器存储。
- [ ] 在 Axios 请求拦截器中附加 `X-CloudWay-Runtime-Settings`，不在日志中输出请求头或值。
- [ ] 运行 `npm run build`，预期 TypeScript 与 Vite 构建成功。

### Task 2: 设置弹窗提示与清除入口

**Files:**
- Modify: `frontend/src/components/NavBar.vue`
- Modify: `frontend/src/i18n/locales/zh.json`
- Modify: `frontend/src/i18n/locales/en.json`
- Modify: `frontend/src/i18n/locales/ja.json`

- [ ] 在设置表单顶部加入“配置仅保存在当前浏览器中，服务器不会保存”提示。
- [ ] 增加带删除图标的“清除配置”按钮，并调用 `clearRuntimeSettings`。
- [ ] 增加中文、英文和日文文案。
- [ ] 运行 `npm run build`，预期构建成功且不存在缺失翻译键。

### Task 3: 后端仅内存运行配置

**Files:**
- Modify: `backend/app/config.py`
- Modify: `backend/app/api/main.py`
- Modify: `backend/app/api/routes/settings.py`

- [ ] 删除 `runtime_settings.json` 的加载与写入逻辑，保留启动环境变量快照作为回退。
- [ ] 实现请求头解码、字段白名单、长度校验和内存配置应用。
- [ ] 在 FastAPI 中间件中读取客户端配置；变化时重置 LLM、地图和旅行规划单例。
- [ ] 将旧 `/api/settings` 路由改为不返回、不持久化任何密钥。
- [ ] 用 Python 导入检查验证后端模块无语法或循环导入错误。

### Task 4: 持久化边界与文档

**Files:**
- Modify: `README.md`
- Verify: `backend/app/api/routes/trip.py`

- [ ] 更新 Docker 部署说明，说明服务器密钥可留空并由用户在浏览器设置。
- [ ] 确认密钥只存在请求头，不进入 `TripRequest.model_dump()` 与 `backend/data/trip_tasks/*.json`。
- [ ] 运行 `git diff --check`、前端构建和后端导入检查。

