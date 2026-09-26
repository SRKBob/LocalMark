export interface PdfInspectionResult {
  success: boolean
  error?: string
  docType?: 'TextBased' | 'Scanned' | 'Mixed' | 'ImageBased' | string
  confidence?: number
  markdown?: string
  items?: TextItem[]
  duration?: number
  pageCount?: number
  pagesNeedingOcr?: number[]
}

export interface TextItem {
  page: number
  x: number
  y: number
  width: number
  height: number
  text: string
  rotation?: number
  fontName?: string
  fontSize?: number
}

export interface ElectronAPI {
  openPdfDialog: () => Promise<string | null>
  readPdfBuffer: (filePath: string) => Promise<ArrayBuffer>
  processPdf: (filePath: string) => Promise<PdfInspectionResult>
  saveMarkdown: (content: string, defaultName: string) => Promise<boolean>
}

declare global {
  interface Window {
    electronAPI: ElectronAPI
  }
}
