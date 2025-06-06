<template>
  <div class="auth-form">
    <form @submit.prevent="handleRegister" autocomplete="off">
      <!-- 🐝 honeypot против автозаполнения -->
      <input type="text" style="display:none;" autocomplete="username">
      <input type="password" style="display:none;" autocomplete="new-password">

      <input
        v-model="username"
        name="username"
        type="text"
        placeholder="Логин"
        autocomplete="off"
        required
      />
      <input
        v-model="email"
        name="email"
        type="email"
        placeholder="Email"
        autocomplete="off"
        required
      />
      <input
        v-model="password"
        name="password"
        type="password"
        placeholder="Пароль"
        autocomplete="new-password"
        required
      />
      <input
        v-model="confirmPassword"
        name="confirm"
        type="password"
        placeholder="Повторите пароль"
        autocomplete="new-password"
        required
      />
      <button type="submit">Принять</button>
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

