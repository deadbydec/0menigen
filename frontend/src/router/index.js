// ✅ Убираем localStorage и достаём токен из куков
import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/store/auth";

// 📌 Функция для получения куки
function getCookie(name) {
  let matches = document.cookie.match(
    new RegExp(
      "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, "\\$1") + "=([^;]*)"
    )
  );
  return matches ? decodeURIComponent(matches[1]) : undefined;
}

// 📌 Импортируем все компоненты
import MainLayout from "@/components/layout/MainLayout.vue";
import HomePage from "@/components/HomePage.vue";
import UserAuth from "@/components/auth/UserAuth.vue";
import UserProfile from "@/components/profile/UserProfile.vue";
import UserInventory from "@/components/UserInventory.vue";
import NewsPage from "@/components/news/NewsPage.vue";
import PlayersSearch from "@/components/PlayersSearch.vue";
import ProfilePage from "@/components/profile/ProfilePage.vue";
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




// 🔥 Определяем маршруты
const routes = [
  {
    path: "/",
    component: MainLayout,
    children: [
      { path: "", redirect: "/home" },
      { path: "login", component: UserAuth },
      { path: "news", component: NewsPage, meta: { requiresAuth: true } },
      { path: "home", component: HomePage, meta: { requiresAuth: true } },     
      { path: "profile", component: UserProfile, meta: { requiresAuth: true } },
      { path: "profile/:id", component: ProfilePage, meta: { requiresAuth: true } },
      { path: "inventory", component: UserInventory, meta: { requiresAuth: true } },
      { path: "events", component: EventsPage, meta: { requiresAuth: true } },
      { path: '/landfill', component: LandfillPage, meta: { requiresAuth: true } },
      { path: '/blackmarket', component: BlackMarket, meta: { requiresAuth: true } },
      { path: '/voidgate', component: VoidGate, meta: { requiresAuth: true } },
      { path: "players", component: PlayersSearch, meta: { requiresAuth: true } },
      
      { path: "mall", component: MallPage, meta: { requiresAuth: true } },
      { path: "mall/:category", component: ShopPage, meta: { requiresAuth: true }, props: true },


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
      {
        path: '/admin',
        name: 'AdminPanel',
        component: () => import('@/components/admin/AdminUserPanel.vue') // путь может отличаться
      },
    ],
  },
  // Можно сделать 404:
  { path: "/:pathMatch(.*)*", redirect: "/home" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();

  if (!authStore.userLoaded) {
    await authStore.fetchUser();
  }

  if (authStore.isLoggedIn && !authStore.user?.race_id && to.path !== "/origin") {
    return next("/origin");
  }

  next();
});

export default router;


