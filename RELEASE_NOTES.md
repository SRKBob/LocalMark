## LocalMark v1.0.0 — 首个正式版本发布

> 本地隐私优先的极速 PDF 转 Markdown 桌面工作台

底层集成 [firecrawl/pdf-inspector](https://github.com/firecrawl/pdf-inspector) 的 Rust 原生解析引擎，**全程纯本地离线运行，文档零外传**。

---

### 📦 下载说明

| 文件 | 类型 | 说明 |
| :--- | :--- | :--- |
| `LocalMark-Setup-1.0.0.exe` | 安装版 | 双击安装，自动创建桌面与开始菜单快捷方式，可自选安装目录 |
| `LocalMark-Portable-1.0.0.exe` | 便携版 | 免安装单文件，双击即用，可放入 U 盘随身携带 |

> 系统要求：Windows 10 / 11 (x64)

---

### ✨ 核心特性

- ⚡ **毫秒级极速解析** — 原生文本型 PDF 200ms 内完成提取，内存占用仅数十 MB，无需 GPU。
- 🛡️ **智能规避无效 OCR** — 10~50ms 抽样分类（`TextBased` / `Scanned` / `Mixed`），约 54% 的原生文本 PDF 直接本地提取，不走耗时昂贵的 OCR 通道。
- 📐 **几何与版面精准还原** — 解析 PDF 文本矩阵变换（`Tm`），恢复真实包围盒（AABB）与旋转角度，解决双栏排版、旋转文字错乱问题。
- 📊 **双模表格识别** — 矢量边框并查集 + 无框文本对齐启发式双引擎。
- 🔍 **沉浸式双栏工作台**
  - 左侧：`PDF.js` 渲染原文档，叠加坐标高亮遮罩层
  - 右侧：Markdown 结构化结果实时编辑，支持一键复制全文与导出 `.md`
- 🔒 **隐私零泄露** — 无任何网络请求，敏感合同 / 财报 / 论文 / 个人笔记可放心处理。

---

### 🛠️ 技术栈

Electron 32 · Vue 3 · Vite 5 · TypeScript · TailwindCSS · PDF.js · @firecrawl/pdf-inspector (Rust N-API)

---

### ✅ 校验信息 (SHA256)

```
c76b5616ad3da156311ffde8c7192cf72ec2ce6e74aea7278f7ef5aab99e550d  LocalMark-Portable-1.0.0.exe
bf780b4cd631150cbdd745e68e9e759bb6505b0f1c02702af50530dcd0971a1d  LocalMark-Setup-1.0.0.exe
```

---

### ⚠️ 已知限制

- 当前安装包**未做代码签名**，首次运行 Windows SmartScreen 可能提示"未知发布者"，点击「更多信息 → 仍要运行」即可。
- 内置 OCR 尚未启用（`Scanned` 类型文档会在状态栏提示需 OCR 介入，暂不自动识别）。
- 目前仅支持单页预览与定位，多页虚拟滚动正在开发中。

---

### 🙏 致谢

- [firecrawl/pdf-inspector](https://github.com/firecrawl/pdf-inspector) — 高性能 Rust PDF 分类 / 提取 / Markdown 转换引擎
- [PDF.js](https://github.com/mozilla/pdf.js) — 开源 PDF 渲染基础设施
- [Electron](https://github.com/electron/electron) · [Vue.js](https://github.com/vuejs/core) — 跨平台桌面与视图框架

**完整变更记录**：https://github.com/SRKBob/LocalMark/commits/main
