import { defineStore } from 'pinia'

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: [],
    maxToasts: 3,
  }),

  actions: {
    addToast(message, options = {}) {
      const id = Date.now() + Math.random()
      if (this.toasts.length >= this.maxToasts) {
        this.toasts.shift()
      }
      const toast = {
        id,
        message,
        type: options.type || 'default',
        duration: options.duration || 20000, // ⏱️ теперь дольше
      }
      this.toasts.push(toast)
      setTimeout(() => {
        this.removeToast(id)
      }, toast.duration)
    },

    removeToast(id) {
      this.toasts = this.toasts.filter(t => t.id !== id)
    },

    success(message, duration = 5000) {
      this.addToast(message, { type: 'success', duration })
    },

    error(message, duration = 6000) {
      this.addToast(message, { type: 'error', duration })
    },
  },
})


