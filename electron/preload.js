const { contextBridge, ipcRenderer } = require('electron')

contextBridge.exposeInMainWorld('electron', {
  sendQuestion: (data) => ipcRenderer.invoke('send-question', data)
})
