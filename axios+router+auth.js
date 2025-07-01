//////utils.axios.js
import axios from 'axios';

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



//////router/index.js
import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/store/auth";
import { h, resolveComponent } from "vue";
function getCookie(name) {
  let matches = document.cookie.match(
    new RegExp(
      "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, "\\$1") + "=([^;]*)"
    )
  );
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

const AppWrapper = {
  render() {
    return h(resolveComponent("router-view"));
  },
};

import AuthLayout from "@/components/layout/AuthLayout.vue";
import HomePage from "@/components/HomePage.vue";
import UserAuth from "@/components/auth/UserAuth.vue";
import UserProfile from "@/components/profile/UserProfile.vue";
import UserInventory from "@/components/UserInventory.vue";
import NewsPage from "@/components/news/NewsPage.vue";
import PlayersSearch from "@/components/PlayersSearch.vue";
import ProfilePublic from "@/components/profile/public/ProfilePublic.vue";
import MallPage from "@/components/mall/MallPage.vue";
import ShopPage from "@/components/mall/ShopPage.vue";
import NeonCircus from "@/components/games/NeonCircus.vue";
import WorldRangs from "@/components/WorldRangs.vue";
import OmegaForum from "@/components/forum/OmegaForum.vue";
import ThreadView from "@/components/forum/ThreadView.vue";
import OriginPage from "@/components/OriginPage.vue";
import EventsPage from "@/components/events/EventsPage.vue";
import LandfillPage from '@/components/events/LandfillPage.vue';
import BlackMarket from '@/components/events/BlackMarket.vue';
import VoidGate from '@/components/events/VoidGate.vue';
import PersonalShop from '@/components/usershop/PersonalShop.vue';
import ShopSearch from '@/components/usershop/ShopSearch.vue';
import UserSafe from '@/components/UserSafe.vue';
import MyPets from '@/components/pets/MyPets.vue';
import PetProfile from '@/components/pets/PetProfile.vue';
import PetWardrobe from '@/components/PetWardrobe.vue';
import VipShop from '@/components/vipshop/VipShop.vue';
import QuestBoard from '@/components/events/quests/QuestBoard.vue';
import NPCQuest from '@/components/events/quests/NPCQuest.vue';
import ClansPage from '@/components/clans/ClansPage.vue';
import AuctionsPage from '@/components/trade/AuctionsPage.vue';

const routes = [
  {
  path: "/login",
  component: AuthLayout,
  children: [
    { path: "", component: UserAuth },
    { path: "home", component: HomePage },
  ]
},
{
  path: "/adminarnia",
  name: "Adminarnia",
  component: () => import("@/components/admin/Adminarnia.vue"),
  meta: { requiresAuth: true }
},
{
  path: "/",
  component: AppWrapper,
  children: [
      { path: "/", redirect: "/home" },
      { path: "news", component: NewsPage, meta: { requiresAuth: true } },
      { path: "home", component: HomePage, meta: { requiresAuth: true } },     
      { path: "profile", component: UserProfile, meta: { requiresAuth: true } },
      { path: "profile/:id", component: ProfilePublic, meta: { requiresAuth: true } },
      { path: "inventory", component: UserInventory, meta: { requiresAuth: true } },
      { path: "events", component: EventsPage, meta: { requiresAuth: true } },
      { path: '/landfill', component: LandfillPage, meta: { requiresAuth: true } },
      { path: '/blackmarket', component: BlackMarket, meta: { requiresAuth: true } },
      { path: '/voidgate', component: VoidGate, meta: { requiresAuth: true } },
      { path: "players", component: PlayersSearch, meta: { requiresAuth: true } },
      { path: "/npc_quests", component: QuestBoard, meta: { requiresAuth: true } },
       {
    path: "/npc_quests/:npcId",
    name: "npc-quest",
    component: NPCQuest,
    meta: { requiresAuth: true }
  },
      { path: '/clans', component: ClansPage, meta: { requiresAuth: true } },
      { path: '/mypets', component: MyPets, meta: { requiresAuth: true } },
      { path: '/pet/:id', component: PetProfile, meta: { requiresAuth: true }, props: true },
      { path: "wardrobe", component: PetWardrobe, meta: { requiresAuth: true } },
      { path: "personalshop", component: PersonalShop, meta: { requiresAuth: true } },
      { path: "shopsearch", component: ShopSearch, meta: { requiresAuth: true } },
      { path: "safe", component: UserSafe, meta: { requiresAuth: true } },
      { path: "mall", component: MallPage, meta: { requiresAuth: true } },
      { path: "mall/:category", component: ShopPage, meta: { requiresAuth: true }, props: true },
      { path: '/vip_shop', component: VipShop, meta: { requiresAuth: true } },
      { path: '/auctions', component: AuctionsPage, meta: { requiresAuth: true } },
      { path: "games", component: NeonCircus, meta: { requiresAuth: true } },
      {
        path: '/games/match3',
        name: 'Match3',
        component: () => import('@/components/games/Match3Game.vue')
      },
      { path: "rangs", component: WorldRangs, meta: { requiresAuth: true } },
      { path: "forum", component: OmegaForum, meta: { requiresAuth: true } },
      { path: "forum/:thread_id", component: ThreadView, meta: { requiresAuth: true } },
      { path: "origin", name: "origin", component: OriginPage, meta: { requiresAuth: true } },
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // ⬇️ вот оно — ключ к жизни
    return { top: 0 }
  }
})

router.afterEach(() => {
  window.scrollTo({ top: 0, behavior: "smooth" });
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore();
  if (!auth.authReady) await auth.fetchUser();

  if (to.meta.requiresAuth && !auth.isAuthenticated) return next("/login");
  next();
});

export default router;


///////store.auth.js
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from "@/utils/axios";
import { useRouter } from 'vue-router'
import { usePlayerStore } from "@/store/player";

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null);
  const isAuthenticated = computed(() => !!user.value);
  const isFetching = ref(false);
  const authReady = ref(false);
  const router = useRouter()

  watch(
    () => useAuthStore.user,
    (user) => {
      if (user && !user.race_id) {
        fetchRaces();
      }
    },
    { immediate: true }
  );

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
    const res = await api.get("/player/");
    if (res.status === 200 && res.data?.name) {
      user.value = res.data.name;
    } else {
      user.value = null;
    }
  } catch (err) {
    console.error("❌ Ошибка fetchUser", err);
    user.value = null;
  } finally {
    isFetching.value = false;
    authReady.value = true;
  }
}

async function logout() {
  try {
    await api.post("/auth/logout", null, { withCredentials: true });
    console.log("✅ Выход успешен!");
  } catch (e) {
    console.error("❌ Ошибка выхода", e);
  } finally {
    const playerStore = usePlayerStore();
    playerStore.resetPlayer?.(); // если есть
    clearAuth();

    // 💣 финальный удар
    window.location.href = "/login"; // переход
    setTimeout(() => {
      window.location.reload();      // + перезапуск UI
    }, 100); // можно даже без задержки
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



