import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  openPdfDialog: () => ipcRenderer.invoke('dialog:openPdf'),
  readPdfBuffer: (filePath: string) => ipcRenderer.invoke('file:readPdfBuffer', filePath),
  processPdf: (filePath: string) => ipcRenderer.invoke('engine:processPdf', filePath),
  saveMarkdown: (content: string, defaultName: string) => ipcRenderer.invoke('file:saveMarkdown', { content, defaultName })
})
