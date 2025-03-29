import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/utils/axios";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);
  const isAuthenticated = computed(() => !!user.value);
  const isFetching = ref(false);
  const authReady = ref(false);


  // Функция регистрации
  const registerUser = async (username, email, password, confirmPassword) => {
    try {
      // Обрати внимание: сервер ожидает confirm_password, а не confirmPassword,
      // но в Pydantic модели ты уже настроила alias. Здесь лучше отправлять именно ключ confirm_password.
      const response = await api.post("/auth/register", { 
        username, 
        email, 
        password, 
        confirm_password: confirmPassword 
      }, { headers: { "Content-Type": "application/json" } });
      console.log("✅ Регистрация успешна!", response.data);
      // Можно по желанию сразу выполнить логин после регистрации:
      // await login(username, password);
    } catch (error) {
      console.error("❌ Ошибка регистрации:", error.response?.data || error.message);
      throw error;
    }
  };
  
  async function login(username, password) {
    await api.post("/auth/login", { username, password });
    // После удачного логина просим бэкенд подтвердить, кто мы
    // 💤 Ждём, чтобы браузер успел установить куку
  await new Promise((res) => setTimeout(res, 100)); 

    await fetchUser();
  }

  async function fetchUser() {
    if (isFetching.value) return;
    isFetching.value = true;
    try {
      const res = await api.get("/player/"); // 🔥 рабочий, защищённый роут
      user.value = res.data.name || null;
    } catch {
      user.value = null;
    } finally {
      isFetching.value = false;
      authReady.value = true;
    }
  }
  


  async function logout() {
    try {
      // Отправляем запрос на сервер для удаления куки (withCredentials важен)
      await api.post("/auth/logout", null, { withCredentials: true });
      console.log("✅ Выход успешен!");
    } catch (error) {
      console.error("⚠️ Ошибка при выходе:", error.response?.data || error.message);
    } finally {
      clearAuth();
      // Добавляем задержку, чтобы куки точно очистились, затем перенаправляем на логин
      setTimeout(() => {
        window.location.replace("/login");
      },
    );
    }
  }
  
  function clearAuth() {
    // Принудительно удаляем все куки
    document.cookie.split(";").forEach((cookie) => {
      const name = cookie.split("=")[0].trim();
      document.cookie = `${name}=;expires=${new Date(0).toUTCString()};path=/;domain=localhost`;
    });
    localStorage.clear();
    sessionStorage.clear();
    
    // Сбрасываем состояние в Pinia
    const authStore = useAuthStore();
    authStore.user = null;
  }
  

  return { user, isAuthenticated, login, logout, fetchUser, isFetching, registerUser, authReady };
});










