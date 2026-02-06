import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useLayoutStore = defineStore('layout', () => {
  // Sidebar collapsed state
  const sidebarCollapsed = ref(false)

  // Toggle sidebar
  function toggleSidebar() {
    sidebarCollapsed.value = !sidebarCollapsed.value
    // Persist to localStorage
    if (sidebarCollapsed.value) {
      localStorage.setItem('sidebar-collapsed', 'true')
    } else {
      localStorage.removeItem('sidebar-collapsed')
    }
  }

  // Initialize from localStorage
  function init() {
    const saved = localStorage.getItem('sidebar-collapsed')
    if (saved === 'true') {
      sidebarCollapsed.value = true
    }
  }

  return {
    sidebarCollapsed,
    toggleSidebar,
    init
  }
})
