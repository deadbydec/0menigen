import { defineStore } from 'pinia';

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: [],
    maxToasts: 3, // 👈 лимит
  }),

  actions: {
    addToast(message, options = {}) {
        const id = Date.now() + Math.random();
        if (this.toasts.length >= this.maxToasts) {
          this.toasts.shift(); // удалим самый старый
        }
      const toast = {
        id,
        message,
        type: options.type || 'default',
        duration: options.duration || 2000,
      };
      this.toasts.push(toast);
      setTimeout(() => {
        this.removeToast(id);
      }, toast.duration);
    },

    removeToast(id) {
      this.toasts = this.toasts.filter(t => t.id !== id);
    }
  }
});
