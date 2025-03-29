// src/store/news.js
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "axios";

export const useNewsStore = defineStore("news", () => {
  const newsList = ref([]); // ✅ Начальное значение - пустой массив
  const categories = ref(["Все", "Обновления", "События", "Баланс", "Фан-контент"]);
  const selectedCategory = ref("Все");
  const activeComments = ref(null);
  const newComment = ref("");

  // ✅ Фильтр новостей (чтобы не было undefined)
  const filteredNews = computed(() => {
    return newsList.value.length > 0
      ? newsList.value.filter((news) => selectedCategory.value === "Все" || news.category === selectedCategory.value)
      : [];
  });

  // ✅ Сортировка по дате
  const sortedNews = computed(() => {
    return filteredNews.value.slice().sort((a, b) => new Date(b.date) - new Date(a.date));
  });

  // ✅ Получение новостей с сервера
  const fetchNews = async (category = "Все") => {
    selectedCategory.value = category;
    try {
      const response = await api.get(`https://localhost:5002/api/news/`, { withCredentials: true });
      newsList.value = response.data || []; // ✅ Обязательно сохраняем массив, даже если пусто
    } catch (error) {
      console.error("Ошибка загрузки новостей:", error);
    }
  };

  // ✅ Лайки
  const likeNews = async (newsId) => {
    try {
      const response = await api.post(`https://localhost:5002/api/news/${newsId}/like`);
      if (response.data.status === "success") {
        const news = newsList.value.find((n) => n.id === newsId);
        if (news) news.likes = response.data.likes;
      }
    } catch (error) {
      console.error("Ошибка при лайке:", error);
    }
  };

  // ✅ Комментарии
  const toggleComments = (newsId) => {
    activeComments.value = activeComments.value === newsId ? null : newsId;
  };

  const addComment = async (newsId) => {
    if (!newComment.value.trim()) return;
    const username = localStorage.getItem("username") || "Аноним";
    try {
      const response = await api.post(`https://localhost:5002/api/news/${newsId}/comment`, {
        author: username,
        text: newComment.value,
      });

      if (response.data.status === "success") {
        const news = newsList.value.find((n) => n.id === newsId);
        if (news) news.comments = response.data.comments;
        newComment.value = "";
      }
    } catch (error) {
      console.error("Ошибка при добавлении комментария:", error);
    }
  };

  return {
    newsList,
    categories,
    selectedCategory,
    activeComments,
    newComment,
    filteredNews,
    sortedNews,
    fetchNews,
    likeNews,
    toggleComments,
    addComment,
  };
});
