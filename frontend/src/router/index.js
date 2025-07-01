// ✅ Убираем localStorage и достаём токен из куков
import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/store/auth";
import { h, resolveComponent } from "vue";

// 📌 Функция для получения куки
function getCookie(name) {
  let matches = document.cookie.match(
    new RegExp(
      "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, "\\$1") + "=([^;]*)"
    )
  );
  return matches ? decodeURIComponent(matches[1]) : undefined;
}
// 👇 Заглушка-обёртка: просто отдаёт <router-view />
const AppWrapper = {
  render() {
    return h(resolveComponent("router-view"));
  },
};

// 📌 Импортируем все компоненты
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
import Adminarnia from '@/components/admin/Adminarnia.vue';
import ClansPage from '@/components/clans/ClansPage.vue';
import AuctionsPage from '@/components/trade/AuctionsPage.vue';

// 🔥 Определяем маршруты
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


