<script setup>
import { useAuthStore } from "@/store/auth";
import { useInboxStore } from "@/store/inbox";
import { ref, computed } from "vue"
import { useRouter } from "vue-router"
import InboxModal from "@/components/inbox/InboxModal.vue";
import { usePlayerStore } from "@/store/player";

const mouseX = ref(0)
const mouseY = ref(0)
const playerStore = usePlayerStore();

//const parallaxStyle = computed(() => {
 // const maxShift = 30 // максимум смещения в px
 // const x = ((mouseX.value - window.innerWidth / 2) / window.innerWidth) * maxShift
 // const y = ((mouseY.value - window.innerHeight / 2) / window.innerHeight) * maxShift
 // return {
 //   transform: `translate(${x}px, ${y}px)`
//  }
//})

//if (typeof window !== 'undefined') {
//  window.addEventListener('mousemove', (e) => {
//    mouseX.value = e.clientX
 //   mouseY.value = e.clientY
//  })
//}

const inboxStore = useInboxStore();
const authStore = useAuthStore();


const router = useRouter()
const profileHovering = ref(false)
const shopHovering = ref(false)
const eventsHovering = ref(false)
const socialHovering = ref(false)
const lentaHovering = ref(false)
const gamesHovering = ref(false)
const rankHovering = ref(false)
const petsHovering = ref(false)
const wardrobeHovering = ref(false)
const clansHovering = ref(false)
const tradeHovering = ref(false)

function goTo(path) {
  router.push(path)
  hovering.value = false
}

const logout = async () => {
  try {
    await authStore.logout(); // куки на бэке удаляются
  } catch (e) {
    console.error("❌ Ошибка при выходе", e);
  } finally {
    playerStore.$reset();
    authStore.user = null;

    // 💥 имитируем F5 + отправляем на логин
    window.location.href = "/login"; // это ПОЛНОСТЬЮ перезагружает всё
  }
}

import logoIcon from "@/assets/LOGO.png"; // второй кристалл
</script>

<template>

    <!-- 🔥 Шапка с навигацией -->
    <header>
      <img :src="logoIcon" alt="-" class="logo-icon" />
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
      <li @click="logout">Выйти</li>
    </ul>
  </div>
</li>

<li class="profile-dropdown" @mouseenter="petsHovering = true" @mouseleave="petsHovering = false">
  <button class="p-2 text-white hover:text-purple-300 transition">
    <font-awesome-icon :icon="['fas', 'paw']" />
  </button>

  <!-- ВЫПАДАЮЩЕЕ МЕНЮ -->
  <div v-if="petsHovering" class="dropdown-menu">
    <ul>
      <li @click="goTo('/mypets')">Мои петы</li>
      <li @click="goTo('/shelter')">Приют</li>
    </ul>
  </div>
</li>

<li class="profile-dropdown" @mouseenter="wardrobeHovering = true" @mouseleave="wardrobeHovering = false">
  <button class="p-2 text-white hover:text-purple-300 transition">
    <font-awesome-icon :icon="['fas', 'hat-wizard']" />
  </button>

  <!-- ВЫПАДАЮЩЕЕ МЕНЮ -->
  <div v-if="wardrobeHovering" class="dropdown-menu">
    <ul>
      <li @click="goTo('/wardrobe')">Гардероб</li>
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
      <li @click="goTo('/npc_quests')">Доска квестов</li>
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

<li class="profile-dropdown" @mouseenter="clansHovering = true" @mouseleave="clansHovering = false">
  <button class="p-2 text-white hover:text-purple-300 transition">
    <font-awesome-icon :icon="['fas', 'fa-shield-heart']" />
  </button>

  <!-- ВЫПАДАЮЩЕЕ МЕНЮ -->
  <div v-if="clansHovering" class="dropdown-menu">
    <ul>
      <li @click="goTo('/clans')">Кланы</li>
      <li @click="goTo('/myclan')">Мой клан</li>
    </ul>
  </div>
</li>

<li class="profile-dropdown" @mouseenter="tradeHovering = true" @mouseleave="tradeHovering = false">
  <button class="p-2 text-white hover:text-purple-300 transition">
    <font-awesome-icon :icon="['fas', 'fa-scale-balanced']" />
  </button>

  <!-- ВЫПАДАЮЩЕЕ МЕНЮ -->
  <div v-if="tradeHovering" class="dropdown-menu">
    <ul>
      <li @click="goTo('/auctions')">Аукционы</li>
      <li @click="goTo('/trades')">Пункт обмена</li>
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
      <li @click="goTo('/players')">Поиск игроков</li>
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

    <!-- 🔥 Модальное окно личных сообщений -->
<InboxModal v-if="inboxStore.isModalOpen" />
</template>

<style scoped lang="scss">

  .logo-icon {
    position: fixed;
    margin-left: -930px;
    margin-top:5px;
  width: 11.5em;
  height: 4.0em;
  vertical-align: -0.2em;
  margin-right: 4px;
  display: inline-block;
}

  header {
    background:linear-gradient(90deg, rgba(14, 224, 214, 0.116), rgba(24, 24, 24, 0.904),  rgba(24, 24, 24, 0.904),rgba(5, 235, 197, 0.13));
    color: white;
    border: 1px solid #d1d1d1cc;
    padding: 5px 0;
    text-align: center;
    width: 100%;
    position: fixed;
    font-family: 'JetBrains Mono', monospace;
    left: 0;
    z-index: 1000;
  }
  
  header {
    box-shadow: 0 4px 6px rgba(0.2, 0.2, 0.2, 0.2);
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
      margin-top: -5px;
      justify-content: center;
      gap: 18px;
  
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
  


  .profile-dropdown {
  position: relative;

  .dropdown-menu {
    position: absolute;
    top: 90%;
    left: 50%;
    transform: translateX(-50%);
    background: #181818e7;
    color: white;
    padding: 5px 4;
    border-radius: 11px;
    border: 1px solid rgb(196, 196, 196);
    min-width: 180px;
    text-align: left;
    z-index: 9999;
    backdrop-filter: blur(7px);

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
          border-radius: 10px;
        }
      }
    }
  }
}
</style>
