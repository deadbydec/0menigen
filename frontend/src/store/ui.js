import { reactive, toRefs } from "vue";

const state = reactive({
  isLoading: false, // Глобальный флаг загрузки
  isDarkMode: localStorage.getItem("darkMode") === "true", // Темная тема
  activeModal: null, // Какая модалка сейчас открыта
});

export const uiState = {
  ...toRefs(state),

  setLoading(value) {
    state.isLoading = value;
  },

  toggleDarkMode() {
    state.isDarkMode = !state.isDarkMode;
    localStorage.setItem("darkMode", state.isDarkMode);
  },

  openModal(modalName) {
    state.activeModal = modalName;
  },

  closeModal() {
    state.activeModal = null;
  },
};
