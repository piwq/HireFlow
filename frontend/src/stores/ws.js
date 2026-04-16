/**
 * Global WebSocket singleton.
 * One connection per session — shared between chat and notifications.
 * ChatView registers a callback via setChatCallback() to receive chat messages.
 */
import { ref } from 'vue'
import { useNotificationsStore } from './notifications.js'

export const wsConnected = ref(false)

let socket = null
let chatCallback = null
let reconnectTimer = null

export function connectWS() {
  const token = localStorage.getItem('token')
  if (!token) return
  if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) return

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const url = `${protocol}//${window.location.host}/api/ws?token=${token}`
  socket = new WebSocket(url)

  socket.onopen = () => { wsConnected.value = true }

  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data)
      if (msg.type === 'notification') {
        if (msg.event === 'new_message') {
          chatCallback?.(msg.data)
          import('./unread.js').then(m => m.loadUnreadCounts())
        }
        useNotificationsStore().add(msg)
      } else {
        chatCallback?.(msg)
      }
    } catch {}
  }

  socket.onclose = () => {
    socket = null
    wsConnected.value = false
    clearTimeout(reconnectTimer)
    reconnectTimer = setTimeout(connectWS, 3000)
  }

  socket.onerror = () => {
    socket?.close()
  }
}

export function disconnectWS() {
  clearTimeout(reconnectTimer)
  socket?.close()
  socket = null
  chatCallback = null
}

export function sendWS(data) {
  if (socket?.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(data))
    return true
  }
  return false
}

export function isConnected() {
  return socket?.readyState === WebSocket.OPEN
}

/** ChatView registers here to receive incoming chat messages */
export function setChatCallback(fn) {
  chatCallback = fn
}

export function clearChatCallback() {
  chatCallback = null
}
