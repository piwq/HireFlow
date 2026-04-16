import { reactive } from 'vue'
import api from '@/api/index.js'

// Shared reactive state for unread message counts
// { [userId]: count }  — unread messages per sender
const unreadCounts = reactive({})

async function loadUnreadCounts() {
  try {
    const { data } = await api.get('/messages/unread-counts')
    // data is { "senderId": count, ... }  with string keys from JSON
    Object.keys(unreadCounts).forEach(k => delete unreadCounts[k])
    Object.entries(data).forEach(([k, v]) => { unreadCounts[k] = v })
  } catch {}
}

function getTotalUnread() {
  return Object.values(unreadCounts).reduce((sum, c) => sum + c, 0)
}

function clearForUser(userId) {
  delete unreadCounts[userId]
}

function incrementForUser(userId) {
  unreadCounts[userId] = (unreadCounts[userId] || 0) + 1
}

export { unreadCounts, loadUnreadCounts, getTotalUnread, clearForUser, incrementForUser }
