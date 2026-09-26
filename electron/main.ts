import { app, BrowserWindow, ipcMain, dialog } from 'electron'
import path from 'node:path'
import fs from 'node:fs'
import {
  detectPdf,
  extractPagesMarkdown,
  extractTextWithPositions
} from '@firecrawl/pdf-inspector'

let win: BrowserWindow | null = null

function createWindow() {
  win = new BrowserWindow({
    title: 'LocalMark',
    width: 1440,
    height: 900,
    minWidth: 1050,
    minHeight: 650,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    },
    titleBarStyle: 'hidden',
    titleBarOverlay: {
      color: '#0f172a',
      symbolColor: '#94a3b8',
      height: 38
    }
  })

  if (process.env.VITE_DEV_SERVER_URL) {
    win.loadURL(process.env.VITE_DEV_SERVER_URL)
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'))
  }
}

app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

// IPC: 选择 PDF 文件
ipcMain.handle('dialog:openPdf', async () => {
  if (!win) return null
  const result = await dialog.showOpenDialog(win, {
    properties: ['openFile'],
    filters: [{ name: 'PDF Documents', extensions: ['pdf'] }]
  })
  if (result.canceled || result.filePaths.length === 0) return null
  return result.filePaths[0]
})

// IPC: 读取 PDF 二进制流 (转为 ArrayBuffer 传输)
ipcMain.handle('file:readPdfBuffer', async (_, filePath: string) => {
  try {
    const buffer = fs.readFileSync(filePath)
    return buffer.buffer.slice(buffer.byteOffset, buffer.byteOffset + buffer.byteLength)
  } catch (err: any) {
    throw new Error(`无法读取文件: ${err.message}`)
  }
})

// IPC: 调用 @firecrawl/pdf-inspector 原生 Rust 核心
ipcMain.handle('engine:processPdf', async (_, filePath: string) => {
  try {
    const buffer = fs.readFileSync(filePath)
    const startTime = Date.now()

    // 1. 快速分类识别 (10~50ms 抽样)
    let docType = 'TextBased'
    let confidence = 1.0
    let pageCount = 1
    let pagesNeedingOcr: number[] = []

    try {
      const detectRes = detectPdf(buffer)
      if (detectRes) {
        docType = detectRes.pdfType || 'TextBased'
        confidence = detectRes.confidence ?? 1.0
        pageCount = detectRes.pageCount || 1
        pagesNeedingOcr = detectRes.pagesNeedingOcr || []
      }
    } catch (e) {
      console.warn('detectPdf 降级:', e)
    }

    // 2. 结构化 Markdown 提取
    let markdown = ''
    try {
      const mdRes = extractPagesMarkdown(buffer)
      if (mdRes && mdRes.pages) {
        markdown = mdRes.pages.map((p: any) => p.markdown || '').join('\n\n---\n\n')
      }
    } catch (e: any) {
      console.warn('extractPagesMarkdown 失败:', e.message)
    }

    // 3. 提取带坐标与旋转角的 TextItems
    let items: any[] = []
    try {
      const rawPos: any = extractTextWithPositions(buffer)
      if (Array.isArray(rawPos)) {
        items = rawPos
      } else if (rawPos && Array.isArray(rawPos.items)) {
        items = rawPos.items
      } else if (rawPos && Array.isArray(rawPos.lines)) {
        items = rawPos.lines
      }
    } catch (e: any) {
      console.warn('提取坐标图元失败:', e.message)
    }

    const duration = Date.now() - startTime

    return {
      success: true,
      docType,
      confidence,
      pageCount,
      pagesNeedingOcr,
      markdown,
      items,
      duration
    }
  } catch (err: any) {
    return {
      success: false,
      error: err.message || 'PDF 解析发生未知异常'
    }
  }
})

// IPC: 保存 Markdown 文件
ipcMain.handle('file:saveMarkdown', async (_, { content, defaultName }: { content: string; defaultName: string }) => {
  if (!win) return false
  const result = await dialog.showSaveDialog(win, {
    defaultPath: defaultName || 'document.md',
    filters: [{ name: 'Markdown Document', extensions: ['md'] }]
  })
  if (result.canceled || !result.filePath) return false
  fs.writeFileSync(result.filePath, content, 'utf-8')
  return true
})
