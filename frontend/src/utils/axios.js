// axios.js
import axios from 'axios';

// 👇 ДОБАВЬ ЭТУ ФУНКЦИЮ ОБЯЗАТЕЛЬНО
function getCookie(name) {
  const matches = document.cookie.match(new RegExp(
    "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});


// ✅ Перехватчик, ВСЕГДА добавляющий CSRF-токен чётко в заголовок
api.interceptors.request.use((config) => {
const csrfToken = getCookie('csrf_access_token'); // 🔥 Теперь работает
if (csrfToken) {
    config.headers["X-CSRF-TOKEN"] = csrfToken;
  }
  return config;
});

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 419) {
      console.warn("⏰ Токен протух, отправляем на логинку...");
      window.location.href = "/login"; // или router.push()
    }
    return Promise.reject(error);
  }
);


export default api;


