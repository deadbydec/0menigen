<script setup>
import { ref } from "vue";
import { useAuthStore } from "@/store/auth";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const username = ref("");
const password = ref("");

async function handleLogin() {
  try {
    await authStore.login(username.value, password.value);
    router.push('/news');
  } catch (error) {
    console.error("Ошибка авторизации:", error.response?.data || error.message);
  }
}

onMounted(() => {
  document.cookie = "access_token_cookie=;expires=" + new Date(0).toUTCString() + ";path=/;";
  document.cookie = "csrf_access_token=;expires=" + new Date(0).toUTCString() + ";path=/;";
});

</script>


<template>
  <div class="auth-form">
    <form @submit.prevent="handleLogin">
      <input v-model="username" placeholder="Логин" required />
      <input v-model="password" type="password" placeholder="Пароль" required />
      <button type="submit">Войти</button>
    </form>
  </div>
</template>


<style lang="scss">
@use "./AuthStyles.scss" as auth;
</style>
