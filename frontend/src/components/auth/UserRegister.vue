<template>
  <div class="auth-form">
    <form @submit.prevent="handleRegister">
      <input v-model="username" placeholder="Логин" required />
      <input v-model="email" type="email" placeholder="Email" required />
      <input v-model="password" type="password" placeholder="Пароль" required />
      <input v-model="confirmPassword" type="password" placeholder="Повторите пароль" required />
      <button type="submit">Зарегистрироваться</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useAuthStore } from "@/store/auth";
import { useRouter } from "vue-router";

const authStore = useAuthStore();
const router = useRouter();

const username = ref("");
const email = ref("");
const password = ref("");
const confirmPassword = ref("");
const errorMessage = ref("");

async function handleRegister() {
  errorMessage.value = "";
  try {
    await authStore.registerUser(username.value, email.value, password.value, confirmPassword.value);
    // Если хочешь сразу залогиниться после регистрации:
    await authStore.login(username.value, password.value);
    router.push("/origin");
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || error.message;
    console.error("❌ Ошибка регистрации:", errorMessage.value);
  }
}
</script>

<style lang="scss">
@use "./AuthStyles.scss" as auth;
</style>

