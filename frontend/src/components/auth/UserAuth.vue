<script setup>
import { onMounted, watch, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from "@/store/auth";
import UserRegister from "./UserRegister.vue";
import UserLogin from "./UserLogin.vue";

const currentComponent = ref("UserLogin");
const authStore = useAuthStore();
const router = useRouter();

onMounted(async () => {
  await authStore.fetchUser();
  document.cookie = "access_token_cookie=;expires=" + new Date(0).toUTCString() + ";path=/;";
  document.cookie = "csrf_access_token=;expires=" + new Date(0).toUTCString() + ";path=/;";
});

watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated) router.push('/news');
});

// 🔄 Переключение между входом и регистрацией
function switchComponent(component) {
  console.log("📌 [DEBUG] Переключаем компонент на:", component);
  currentComponent.value = component;
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <h2 v-if="currentComponent === 'UserLogin'">Вход</h2>
      <h2 v-else>Регистрация</h2>

      <!-- 🔄 Переключаем компонент динамически -->
      <transition name="fade" mode="out-in">
        <component :is="currentComponent === 'UserLogin' ? UserLogin : UserRegister"></component>
      </transition>

      <!-- 🔀 Кнопки переключения -->
      <div class="auth-switch">
        <button v-if="currentComponent === 'UserRegister'" @click="switchComponent('UserLogin')">
          Уже есть аккаунт?
        </button>
        <button v-if="currentComponent === 'UserLogin'" @click="switchComponent('UserRegister')">
          Нет аккаунта?
        </button>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
@use "./AuthStyles.scss" as auth;
</style>
