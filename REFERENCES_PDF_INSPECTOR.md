# 调研报告与实施方案参考：firecrawl/pdf-inspector

> 来源：WorkBuddy 调研存档 (https://workbuddy.link/p/QxbnFWDIYd7l5ebNkUJ9zw)

---

## 1. 项目核心概述
- **仓库地址**：`https://github.com/firecrawl/pdf-inspector`
- **核心定位**：Firecrawl 开源的高性能 PDF 分类、文本提取与 Markdown 转换引擎（底层纯 Rust 编写）。
- **核心价值**：
  - **极速**：在 200ms 内完成原生文本 PDF 解析。
  - **避开无效 OCR**：约 54% 的 PDF 本身即是可直接提取文本的 Native PDF，通过 10-50ms 轻量抽样检测（`Sample(8)` / `EarlyExit`）识别 `TextBased`、`Scanned`、`Mixed`，避免盲目送入昂贵耗时的 OCR。
  - **几何与阅读顺序还原**：文本矩阵 `Tm` 变换计算真实外接矩形（AABB）和旋转角，解决双栏排版与旋转字错乱。
  - **双模表格检测**：矢量边框并查集（Union-Find）+ 无框文本对齐启发式。
  - **跨语言生态**：Rust 原生、Python (`PyO3`/`maturin`)、Node.js (`napi-rs` `@firecrawl/pdf-inspector`)、WebAssembly (`@firecrawl/pdf-inspector-wasm`)。

---

## 2. 选定产品定位方案：纯本地/零泄露的本地 PDF 转 Markdown 工具（MarkVault / LocalMark）

### 2.1 核心设计理念
1. **零服务端依赖（Zero-Server / Local-First）**：
   - 彻底阻断外部网络上传，纯本地算力（WASM 或本地 Node/Tauri），保证企业合同、财务研报、个人文档绝对隐私。
2. **渐进式解析流**：
   - L1 快速层：`pdf-inspector-wasm` 或 `@firecrawl/pdf-inspector`（200ms 内提取文本、标题 H1-H4、双模表格并转 Markdown）。
   - L2 选择性 OCR 层（按需）：对检测器标出的 `pages_needing_ocr` 单页，按需触发端侧轻量 OCR。
3. **沉浸式双栏工作台**：
   - 左侧：PDF 视图（基于 PDF.js），高亮叠加层。
   - 右侧：实时 Markdown 预览与编辑器。
   - 双向联动互锁：利用 `TextItem` 的 AABB 坐标，点击 Markdown 片段即可在左侧 PDF 原文上高亮定位，反向点选 PDF 区域跳转右侧对应文本。

---

## 3. 落地实施路线与架构模块划分
- **Web Worker 隔离**：WASM 加载和复杂解析放 Worker，主线程保持 60fps。
- **内存优化**：超大文档分批分页流式读取，避免 32 位 WASM 2GB/4GB 内存溢出。
- **CJK 字体支持**：集成 `external/bcmaps`（预置二进制 CMap），防止中文/日文 CID 字体解析乱码。
- **打包交付**：
  - Web/PWA 版本：离线 Service Worker。
  - 桌面客户端版本：Tauri 2.0 / Electron，直接调用原生 Rust crate 或 Node-API，性能更极致。
