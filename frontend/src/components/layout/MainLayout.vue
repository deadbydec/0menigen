<script setup>
import { useAuthStore } from "@/store/auth";
import { useInboxStore } from "@/store/inbox";
import InboxModal from "@/components/inbox/InboxModal.vue";

const inboxStore = useInboxStore();
const authStore = useAuthStore();

function logout() {
  authStore.logout();
}

function login() {
  console.log("Login clicked"); // Дебаг
  authStore.login("дырбулщищ", "898939"); // 🚪 прямой вход
}
</script>

<template>
  <div class="layout">
    <!-- 🔥 Шапка с навигацией -->
    <header>
      <nav>
        <ul>


          <!-- Проверка авторизации -->
          <template v-if="authStore.isAuthenticated">
            <li><router-link to="/news"><font-awesome-icon :icon="['fas', 'newspaper']" /></router-link></li>
            <li><router-link to="/profile"><font-awesome-icon :icon="['fas', 'user']" /></router-link></li>
            <li><router-link to="/inventory"><font-awesome-icon :icon="['fas', 'box']" /></router-link></li>
            <li><router-link to="/games"><font-awesome-icon :icon="['fas', 'gamepad']" /></router-link></li>
            <li><router-link to="/rangs"><font-awesome-icon :icon="['fas', 'trophy']" /></router-link></li>
            <li><router-link to="/mall"><font-awesome-icon :icon="['fas', 'store']" /></router-link></li>
            <li><router-link to="/forum"><font-awesome-icon :icon="['fas', 'comments']" /></router-link></li>
            <li><router-link to="/players"><font-awesome-icon :icon="['fas', 'users']" /></router-link></li>
            <!-- 🔥 Фиксим кнопку "Личные сообщения" -->
            <li><button @click="inboxStore.openModal()"><font-awesome-icon :icon="['fas', 'inbox']" /></button></li>            
            <li><button @click="logout"><font-awesome-icon :icon="['fas', 'sign-out-alt']" /></button></li>
          </template>
            
          
          <li v-if="authStore.isAuthenticated">Привет, {{ authStore.user }}!</li>
          <!-- Если не авторизован -->
          
          
          <template v-else>
            <li><router-link to="/"><font-awesome-icon :icon="['fas', 'home']" /></router-link></li>
            <li><button @click="login"><font-awesome-icon :icon="['fas', 'sign-in-alt']" /></button></li>
          </template>
        </ul>
      </nav>
    </header>

    <!-- 🔥 Основной контент -->
    <main>
      <router-view></router-view>
    </main>

    <!-- 🔥 Модальное окно личных сообщений -->
<InboxModal v-if="inboxStore.isModalOpen" />


    <!-- 🔥 Футер -->
    <footer>
      <p>&copy; 2024 OmezhekNet. Все права защищены.</p>
    </footer>
  </div>
</template>



<style lang="scss">
html, body {
    margin: 0;
    padding: 0;
    height: 100%;
    overflow: hidden;
  }
  
  .layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: url('/images/Neon_Circus1.png') no-repeat center center fixed;
    background-size: cover;
  }
  
  header, footer {
    background-color: rgba(0, 0, 0, 0.459);
    color: white;
    padding: 6px 0;
    text-align: center;
    width: 100%;
    position: fixed;
    left: 0;
    z-index: 1000;
  }
  
  header {
    top: 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  }
  
  footer {
    bottom: 0;
    box-shadow: 0 -4px 6px rgba(0, 0, 0, 0.2);
  }
  
  nav {
    ul {
      display: flex;
      list-style: none;
      padding: 0;
      margin: 0;
      justify-content: center;
      gap: 15px;
  
      li {
        display: inline-block;
        transition: transform 0.2s ease-in-out;
  
        a, button {
          display: flex;
          align-items: center;
          gap: 8px;
          color: white;
          text-decoration: none;
          font-size: 22px;
          padding: 10px 15px;
          background: none;
          border: none;
          cursor: pointer;
          transition: all 0.3s ease;
          
          &:hover {
            opacity: 0.8;
            transform: scale(1.1);
          }
        }
      }
    }
  }
  
  main {
    flex: 1;
    padding: 30px;
    color: white;
    font-family: Arial, sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    width: 100%;
    height: 100%;
    overflow-y: auto;
    padding-top: 60px;
    padding-bottom: 40px;
  }
</style>


