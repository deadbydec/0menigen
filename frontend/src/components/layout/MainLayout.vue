<script setup>
import { useAuthStore } from "@/store/auth";
import { useInboxStore } from "@/store/inbox";
import { ref } from "vue"
import { useRouter } from "vue-router"
import InboxModal from "@/components/inbox/InboxModal.vue";

const mouseX = ref(0)
const mouseY = ref(0)

const parallaxStyle = computed(() => {
  const maxShift = 30 // максимум смещения в px
  const x = ((mouseX.value - window.innerWidth / 2) / window.innerWidth) * maxShift
  const y = ((mouseY.value - window.innerHeight / 2) / window.innerHeight) * maxShift
  return {
    transform: `translate(${x}px, ${y}px)`
  }
})

if (typeof window !== 'undefined') {
  window.addEventListener('mousemove', (e) => {
    mouseX.value = e.clientX
    mouseY.value = e.clientY
  })
}

const inboxStore = useInboxStore();
const authStore = useAuthStore();


function login() {
  console.log("Login clicked"); // Дебаг
  authStore.login("дырбулщищ", "898939"); // 🚪 прямой вход
}

const router = useRouter()
const profileHovering = ref(false)
const shopHovering = ref(false)
const eventsHovering = ref(false)
const socialHovering = ref(false)
const lentaHovering = ref(false)
const gamesHovering = ref(false)
const rankHovering = ref(false)

function goTo(path) {
  router.push(path)
  hovering.value = false
}

function logout() {
  authStore.logout()
  hovering.value = false
}
</script>

<template>
  <div class="bg-parallax" :style="parallaxStyle"></div>
  <div class="layout">
    <!-- 🔥 Шапка с навигацией -->
    <header>
      <nav>
        <ul>


          <!-- Проверка авторизации -->
          <template v-if="authStore.isAuthenticated">
            <li class="profile-dropdown" @mouseenter="lentaHovering = true" @mouseleave="lentaHovering = false">
  <button class="p-2 text-white hover:text-purple-300 transition">
    <font-awesome-icon :icon="['fas', 'rss']" />
  </button>

  <!-- ВЫПАДАЮЩЕЕ МЕНЮ -->
  <div v-if="lentaHovering" class="dropdown-menu">
    <ul>
      <li @click="goTo('/news')">Новости</li>
      <li @click="goTo('/about')">Об игре</li>
    </ul>
  </div>
</li>
            <!-- ОБЁРТКА ДЛЯ ИКОНКИ ПРОФИЛЯ С МЕНЮ -->

            <li class="profile-dropdown" @mouseenter="profileHovering = true" @mouseleave="profileHovering = false">
  <button class="p-2 text-white hover:text-purple-300 transition">
    <font-awesome-icon :icon="['fas', 'id-card']" />
  </button>

  <!-- ВЫПАДАЮЩЕЕ МЕНЮ -->
  <div v-if="profileHovering" class="dropdown-menu">
    <ul>
      <li @click="goTo('/profile')">Профиль</li>
      <li @click="goTo('/personalshop')">Личный магазин</li>
      <li @click="goTo('/inventory')">Инвентарь</li>
      <li @click="goTo('/safe')">Сейф</li>
      <li @click="goTo('/toilet')">Мой туалет</li>
      <li @click="logout">Выйти</li>
    </ul>
  </div>
</li>

<li class="profile-dropdown" @mouseenter="eventsHovering = true" @mouseleave="eventsHovering = false">
  <button class="p-2 text-white hover:text-purple-300 transition">
    <font-awesome-icon :icon="['fas', 'compass']" />
  </button>

  <!-- ВЫПАДАЮЩЕЕ МЕНЮ -->
  <div v-if="eventsHovering" class="dropdown-menu">
    <ul>
      <li @click="goTo('/events')">Интересные места</li>
      <li @click="goTo('/events/season')">Сезонные события</li>
    </ul>
  </div>
</li>


<li class="profile-dropdown" @mouseenter="gamesHovering = true" @mouseleave="gamesHovering = false">
  <button class="p-2 text-white hover:text-purple-300 transition">
    <font-awesome-icon :icon="['fas', 'dice']" />
  </button>

  <!-- ВЫПАДАЮЩЕЕ МЕНЮ -->
  <div v-if="gamesHovering" class="dropdown-menu">
    <ul>
      <li @click="goTo('/games')">Мини-игры</li>
      <li @click="goTo('/lottery')">Лотерея</li>
    </ul>
  </div>
</li>

<li class="profile-dropdown" @mouseenter="rankHovering = true" @mouseleave="rankHovering = false">
  <button class="p-2 text-white hover:text-purple-300 transition">
    <font-awesome-icon :icon="['fas', 'trophy']" />
  </button>

  <!-- ВЫПАДАЮЩЕЕ МЕНЮ -->
  <div v-if="rankHovering" class="dropdown-menu">
    <ul>
      <li @click="goTo('/rangs')">Рейтинги</li>
      <li @click="goTo('/records')">Рекорды</li>
      <li @click="goTo('/comingsoon')">Конкурсы</li>
    </ul>
  </div>
</li>
            <!-- ОБЁРТКА ДЛЯ ИКОНКИ МАГАЗИНА С МЕНЮ -->
<li class="profile-dropdown" @mouseenter="shopHovering = true" @mouseleave="shopHovering = false">
  <button class="p-2 text-white hover:text-purple-300 transition">
    <font-awesome-icon :icon="['fas', 'store']" />
  </button>

  <!-- ВЫПАДАЮЩЕЕ МЕНЮ -->
  <div v-if="shopHovering" class="dropdown-menu">
    <ul>
      <li @click="goTo('/mall')">Торговый центр</li>
      <li @click="goTo('/shopsearch')">Поиск товаров</li>
      <li @click="goTo('/vip_shop')">VIP-шоппинг</li>
    </ul>
  </div>
</li>
<li class="profile-dropdown" @mouseenter="socialHovering = true" @mouseleave="socialHovering = false">
  <button class="p-2 text-white hover:text-purple-300 transition">
    <font-awesome-icon :icon="['fas', 'poo']" />
  </button>

  <!-- ВЫПАДАЮЩЕЕ МЕНЮ -->
  <div v-if="socialHovering" class="dropdown-menu">
    <ul>
      <li @click="goTo('/forum')">Игровой форум</li>
      <li @click="goTo('/clans')">Кланы</li>
      <li @click="goTo('/players')">Поиск игроков</li>
      <li @click="goTo('/toilet/public')">Туалеты</li>
    </ul>
  </div>
</li>
            <!-- 🔥 Фиксим кнопку "Личные сообщения" -->
            <li><button @click="inboxStore.openModal()"><font-awesome-icon :icon="['fas', 'envelope']" /></button></li>            
          </template>
            
          
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

.bg-parallax {
  position: fixed;
  top: -50px;
  left: -50px;
  width: calc(100vw + 100px);
  height: calc(100vh + 100px);
  background: url('/images/blackhole3.jpg') no-repeat center center;
  background-size: cover;
  z-index: -1;
  transition: transform 0.4s ease-out;
  pointer-events: none;
  will-change: transform;
  overflow: hidden;
}

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
            background-color: transparent;
            transform: scale(1.1);
          }
        }
      }
    }
  }
  
  main {
    zoom: 0.9;
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

  .profile-dropdown {
  position: relative;

  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    background-color: rgba(0, 0, 0, 0.425);
    color: white;
    padding: 8px 0;
    border-radius: 8px;
    border: 1px solid rgb(0, 0, 0);
    min-width: 180px;
    text-align: left;
    z-index: 9999;
    box-shadow: 0 8px 12px rgba(0, 0, 0, 0.4);
    backdrop-filter: blur(4px);

    ul {
      list-style: none;
      margin: 0;
      padding: 0;

      li {
        padding: 8px 16px;
        cursor: pointer;
        font-size: 14px;
        white-space: nowrap;

        &:hover {
          background-color: rgba(255, 255, 255, 0.1);
        }
      }
    }
  }
}
</style>


