# LocalMark (墨穹)

> 本地隐私优先的极速 PDF 转 Markdown 桌面工作台

[![Release](https://img.shields.io/github/v/release/SRKBob/LocalMark?label=release&color=2563eb)](https://github.com/SRKBob/LocalMark/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/SRKBob/LocalMark/total?label=downloads&color=4f46e5)](https://github.com/SRKBob/LocalMark/releases)
[![Platform](https://img.shields.io/badge/platform-Windows%20x64-0078D6?logo=windows)](https://github.com/SRKBob/LocalMark/releases/latest)
[![License](https://img.shields.io/github/license/SRKBob/LocalMark?color=22c55e)](./LICENSE)

基于 Electron 32 + Vue 3 + Vite 构建，底层集成 Firecrawl 官方开源的 `@firecrawl/pdf-inspector`（Rust 原生 N-API 引擎）。专为隐私敏感文档（商业合同、财务报表、科研论文、个人笔记）打造，**纯本地离线解析，零数据外传**。

---

## 📥 下载安装

前往 [**Releases 页面**](https://github.com/SRKBob/LocalMark/releases/latest) 下载最新版本：

| 文件 | 类型 | 说明 |
| :--- | :--- | :--- |
| `LocalMark-Setup-x.y.z.exe` | 安装版 | 双击安装，自动创建桌面与开始菜单快捷方式，可自选安装目录 |
| `LocalMark-Portable-x.y.z.exe` | 便携版 | 免安装单文件，双击即用，可放入 U 盘随身携带 |

> 系统要求：Windows 10 / 11 (x64)
> ⚠️ 安装包未做代码签名，首次运行若遇 SmartScreen 提示，点击「更多信息 → 仍要运行」即可。

---

## ✨ 核心特性

- ⚡ **毫秒级极速解析**：原生文本型 PDF 在 200ms 内完成解析，内存占用低至数十 MB。
- 🛡️ **智能避坑，拒绝无效 OCR**：内置 10~50ms 抽样分类检测（`TextBased` / `Scanned` / `Mixed`），约 54% 的原生文本 PDF 无需走耗时且昂贵的 OCR。
- 📐 **几何与版面还原**：全面解析 PDF 文本矩阵变换（`Tm`），恢复真实包围盒（AABB）与旋转角度，解决双栏排版错乱。
- 📊 **双模表格识别**：结合矢量绘制并查集与无框文本对齐启发式算法。
- 🔍 **沉浸式双栏工作台**：
  - 左侧：基于 `PDF.js` 渲染原文档，内置坐标映射与黄色高亮锚点。
  - 右侧：实时 Markdown 结构化预览与编辑器，支持一键全量复制与导出保存。
- 📦 **开箱即用，免安装便携**：支持直接构建 Windows 单文件绿色免安装 EXE。

---

## 🛠️ 技术架构

- **Shell & 运行时**：Electron 32, Node.js 22
- **前端视图层**：Vue 3 (Composition API), Vite 5, TypeScript, TailwindCSS
- **PDF 矢量渲染**：`pdfjs-dist`
- **解析内核**：`@firecrawl/pdf-inspector` (Rust 原生绑定)
- **桌面端打包**：`electron-builder`

---

## 🚀 快速上手

### 环境准备
- Node.js >= 20.0.0
- npm / pnpm / yarn

### 安装依赖
```bash
npm install
```

### 开发环境调试
```bash
npm run dev
```

### 打包 Windows 可执行程序

```bash
npm run build:portable   # 仅打包便携版单文件 EXE
npm run build:setup      # 仅打包 NSIS 安装版 EXE
npm run build:win        # 同时产出便携版 + 安装版
```

构建产物位于 `release/` 目录：

- `LocalMark-Portable-<version>.exe` — 绿色免安装版
- `LocalMark-Setup-<version>.exe` — 安装版

### 应用图标

应用图标由脚本生成（圆角渐变底 + LM 标识）：

```bash
npm run icon    # 依赖 Python Pillow，输出 build/icon.ico 与 build/icon.png
```

### 发布新版本到 GitHub Releases

```bash
# 1. 提升 package.json 中的 version，并重新构建
npm run build:win

# 2. 计算校验值（可选）
sha256sum release/*.exe

# 3. 创建 Release 并上传产物（自动从 git 凭据读取 token）
python scripts/publish_release.py \
  --tag v1.0.0 \
  --name "LocalMark v1.0.0" \
  --notes-file RELEASE_NOTES.md \
  --assets release/LocalMark-Portable-1.0.0.exe \
           release/LocalMark-Setup-1.0.0.exe
```

也可以在 **Actions → Build Windows Release → Run workflow** 中手动触发云端构建，
由 CI 自动产出 Windows 安装包并发布到 Release。

---

## 📄 License
MIT License

---

## 🙏 致谢 (Acknowledgements)

LocalMark 的实现离不开开源社区优秀项目的支持，特别致谢：

- [firecrawl/pdf-inspector](https://github.com/firecrawl/pdf-inspector) — 优秀的纯 Rust 高性能 PDF 分类、文本提取与 Markdown 转换引擎。
- [PDF.js](https://github.com/mozilla/pdf.js) — 强大的开源网页与客户端 PDF 渲染基础设施。
- [Electron](https://github.com/electron/electron) 与 [Vue.js](https://github.com/vuejs/core) — 提供稳定出色的跨平台桌面交互体验。

