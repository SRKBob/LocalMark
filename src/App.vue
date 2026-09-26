<template>
  <div class="flex flex-col h-screen w-screen bg-slate-100 font-sans select-none overflow-hidden">
    <!-- 顶部标题栏与操作菜单 -->
    <header class="h-10 bg-slate-900 text-slate-200 flex items-center justify-between px-4 shrink-0 shadow-md" style="-webkit-app-region: drag">
      <!-- 左侧：产品标识与隐私勋章 -->
      <div class="flex items-center space-x-2.5">
        <div class="w-6 h-6 rounded bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white font-black text-xs shadow-sm">
          LM
        </div>
        <span class="font-bold tracking-wide text-sm bg-gradient-to-r from-blue-300 via-indigo-200 to-white bg-clip-text text-transparent">LocalMark</span>
        <span class="text-[10px] text-slate-400 font-mono">v1.0.0</span>
        <span class="px-2 py-0.5 text-[10px] rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
          纯本地·零泄露
        </span>
      </div>

      <!-- 右侧：文档状态与核心操作按钮 -->
      <div class="flex items-center space-x-3 text-xs" style="-webkit-app-region: no-drag">
        <span v-if="filePath" class="text-slate-400 max-w-[200px] truncate" :title="filePath">
          {{ fileName }}
        </span>
        
        <span v-if="docType" :class="docTypeBadgeClass" class="px-2 py-0.5 rounded font-mono font-medium text-[11px] shadow-sm">
          {{ docType }} ({{ Math.round((confidence || 1) * 100) }}%)
        </span>

        <button 
          @click="openFile" 
          :disabled="isProcessing"
          class="px-3 py-1 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded transition shadow-sm disabled:opacity-50 flex items-center space-x-1"
        >
          <span>打开 PDF</span>
        </button>

        <button 
          @click="exportMarkdown" 
          :disabled="!markdown"
          class="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded transition disabled:opacity-40"
        >
          导出 Markdown
        </button>
      </div>
    </header>

    <!-- 工作区主体 -->
    <main class="flex-1 flex overflow-hidden">
      <!-- 空白欢迎面板 -->
      <div 
        v-if="!filePath" 
        class="flex-1 flex flex-col items-center justify-center p-8 bg-slate-50 border-2 border-dashed border-slate-300 m-4 rounded-xl text-center space-y-4"
      >
        <div class="w-16 h-16 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-inner text-3xl font-bold">
          ⚡
        </div>
        <div class="space-y-1.5">
          <h2 class="text-xl font-bold text-slate-800">打开本地 PDF 即刻体验毫秒级转换</h2>
          <p class="text-sm text-slate-500 max-w-lg leading-relaxed">
            内置 Firecrawl pdf-inspector 原生 Rust 引擎，智能避开无效 OCR，支持双模表格识别与双向坐标溯源，文档绝对不离开本机。
          </p>
        </div>
        <button 
          @click="openFile" 
          class="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded-lg shadow-md transition transform active:scale-95 flex items-center space-x-2"
        >
          <span>选择本地 PDF 开始</span>
        </button>
      </div>

      <!-- 双栏对比主界面 -->
      <template v-else>
        <!-- 左侧：PDF 视图面板 -->
        <div class="w-1/2 flex flex-col border-r border-slate-200 bg-slate-200/60 relative">
          <div class="h-9 bg-slate-200/90 px-3 flex items-center justify-between text-xs text-slate-700 font-medium border-b border-slate-300">
            <div class="flex items-center space-x-2">
              <span class="font-bold">原 PDF 矢量视图</span>
              <span v-if="totalPages > 0" class="text-slate-500">共 {{ totalPages }} 页</span>
            </div>
            <div class="flex items-center space-x-2 text-[11px] text-slate-500">
              <span>缩放: 100%</span>
              <span>•</span>
              <span>支持图元坐标定位</span>
            </div>
          </div>

          <div class="flex-1 overflow-auto p-4 flex justify-center" id="pdf-scroll-viewport">
            <div class="relative bg-white shadow-xl rounded overflow-hidden" ref="canvasContainer">
              <canvas ref="pdfCanvasRef" class="block"></canvas>
              <!-- 交互高亮遮罩图层 -->
              <div 
                v-if="highlightBox" 
                class="absolute border-2 border-amber-500 bg-amber-400/25 rounded pointer-events-none transition-all duration-200 shadow-sm"
                :style="highlightBoxStyle"
              ></div>
            </div>
          </div>
        </div>

        <!-- 右侧：Markdown 结构化结果与编辑面板 -->
        <div class="w-1/2 flex flex-col bg-white">
          <div class="h-9 bg-slate-100 px-3 flex items-center justify-between text-xs text-slate-700 font-medium border-b border-slate-200">
            <div class="flex items-center space-x-3">
              <span class="font-bold text-slate-800">Markdown 提取结果</span>
              <span v-if="parseDuration !== null" class="text-[11px] text-emerald-600 font-mono">
                解析耗时: {{ parseDuration }}ms
              </span>
              <span v-if="items.length > 0" class="text-[11px] text-slate-500">
                识别图元: {{ items.length }} 项
              </span>
            </div>
            <div class="flex items-center space-x-2">
              <button 
                @click="copyMarkdown" 
                class="px-2.5 py-1 text-xs text-slate-600 hover:text-slate-900 border border-slate-300 rounded hover:bg-slate-50 transition"
              >
                {{ copyStatus ? '已复制！' : '复制全文' }}
              </button>
            </div>
          </div>
          
          <!-- 编辑与实时预览区 -->
          <div class="flex-1 flex flex-col overflow-hidden relative">
            <textarea 
              v-model="markdown" 
              class="flex-1 p-4 font-mono text-sm leading-relaxed text-slate-800 focus:outline-none resize-none overflow-auto border-none selection:bg-blue-100"
              placeholder="正在解析或该文档无文本内容..."
              spellcheck="false"
            ></textarea>
          </div>
        </div>
      </template>
    </main>

    <!-- 底部状态栏 -->
    <footer class="h-6 bg-slate-900 text-slate-400 text-[11px] px-3 flex items-center justify-between border-t border-slate-800 shrink-0 font-mono">
      <div class="flex items-center space-x-3">
        <span>引擎：Firecrawl pdf-inspector (Rust Native)</span>
        <span class="text-slate-600">|</span>
        <span v-if="pagesNeedingOcr.length > 0" class="text-amber-400">
          注意：第 {{ pagesNeedingOcr.join(', ') }} 页需 OCR 介入
        </span>
        <span v-else class="text-emerald-400">纯文本流无损还原</span>
      </div>
      <div>
        <span v-if="isProcessing" class="text-amber-400 animate-pulse font-sans">正在极速提取中...</span>
        <span v-else class="text-emerald-400">状态：就绪 (Ready)</span>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import * as pdfjsLib from 'pdfjs-dist'

// 配置 PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.js',
  import.meta.url
).toString()

const filePath = ref<string | null>(null)
const fileName = computed(() => filePath.value ? filePath.value.split(/[\\/]/).pop() : '')
const isProcessing = ref(false)
const docType = ref<string>('')
const confidence = ref<number>(1)
const markdown = ref<string>('')
const totalPages = ref(1)
const pagesNeedingOcr = ref<number[]>([])
const parseDuration = ref<number | null>(null)
const copyStatus = ref(false)
const items = ref<any[]>([])

const pdfCanvasRef = ref<HTMLCanvasElement | null>(null)
const canvasContainer = ref<HTMLDivElement | null>(null)
const highlightBox = ref<{ x: number; y: number; width: number; height: number } | null>(null)

const highlightBoxStyle = computed(() => {
  if (!highlightBox.value) return {}
  return {
    left: `${highlightBox.value.x}px`,
    top: `${highlightBox.value.y}px`,
    width: `${highlightBox.value.width}px`,
    height: `${highlightBox.value.height}px`
  }
})

const docTypeBadgeClass = computed(() => {
  if (docType.value === 'TextBased') return 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
  if (docType.value === 'Scanned') return 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
  return 'bg-blue-500/20 text-blue-300 border border-blue-500/40'
})

const renderPdfPreview = async (path: string) => {
  try {
    const arrayBuffer = await window.electronAPI.readPdfBuffer(path)
    const loadingTask = pdfjsLib.getDocument({ data: new Uint8Array(arrayBuffer) })
    const pdfDoc = await loadingTask.promise
    totalPages.value = pdfDoc.numPages

    // 默认高保真渲染首页
    const page = await pdfDoc.getPage(1)
    const viewport = page.getViewport({ scale: 1.5 })
    
    if (pdfCanvasRef.value) {
      const canvas = pdfCanvasRef.value
      const context = canvas.getContext('2d')
      if (context) {
        canvas.height = viewport.height
        canvas.width = viewport.width

        await page.render({
          canvasContext: context,
          viewport: viewport
        }).promise

        // 如果提取到了图元位置，默认高亮首个关键标题区域示范双向联动
        if (items.value && items.value.length > 0) {
          const first = items.value[0]
          // 坐标映射：PDF 坐标系 (Y从下到上) 转为 Canvas 坐标系 (Y从上到下)
          const scale = 1.5
          const canvasX = first.x * scale
          const canvasY = (viewport.height / scale - first.y - first.height) * scale
          highlightBox.value = {
            x: canvasX,
            y: canvasY,
            width: first.width * scale,
            height: first.height * scale
          }
        }
      }
    }
  } catch (err: any) {
    console.error('PDF.js 渲染预览失败:', err)
  }
}

const openFile = async () => {
  if (!window.electronAPI) {
    alert('请在 Electron 环境中运行')
    return
  }
  const selected = await window.electronAPI.openPdfDialog()
  if (!selected) return

  filePath.value = selected
  isProcessing.value = true
  highlightBox.value = null

  try {
    const res = await window.electronAPI.processPdf(selected)
    if (res.success) {
      docType.value = res.docType || 'TextBased'
      confidence.value = res.confidence ?? 1.0
      markdown.value = res.markdown || ''
      items.value = res.items || []
      parseDuration.value = res.duration ?? 0
      pagesNeedingOcr.value = res.pagesNeedingOcr || []

      // 渲染 PDF.js 预览图层
      await renderPdfPreview(selected)
    } else {
      alert(`解析失败: ${res.error}`)
    }
  } catch (err: any) {
    alert(`处理异常: ${err.message}`)
  } finally {
    isProcessing.value = false
  }
}

const copyMarkdown = async () => {
  if (!markdown.value) return
  await navigator.clipboard.writeText(markdown.value)
  copyStatus.value = true
  setTimeout(() => {
    copyStatus.value = false
  }, 2000)
}

const exportMarkdown = async () => {
  if (!markdown.value || !window.electronAPI) return
  const defaultName = (fileName.value || 'document').replace(/\.pdf$/i, '.md')
  await window.electronAPI.saveMarkdown(markdown.value, defaultName)
}
</script>
