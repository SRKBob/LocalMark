# LocalMark (墨穹)

> 本地隐私优先的极速 PDF 转 Markdown 桌面工作台

基于 Electron 32 + Vue 3 + Vite 构建，底层集成 Firecrawl 官方开源的 `@firecrawl/pdf-inspector`（Rust 原生 N-API 引擎）。专为隐私敏感文档（商业合同、财务报表、科研论文、个人笔记）打造，**纯本地离线解析，零数据外传**。

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

### 打包 Windows 单文件绿色版 (.exe)
```bash
npm run build:portable
```
构建完成后产物位于 `release/LocalMark 1.0.0.exe`。

---

## 📄 License
MIT License
