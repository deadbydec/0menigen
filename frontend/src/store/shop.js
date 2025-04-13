// store/shop.js

import { defineStore } from "pinia";
import { ref } from "vue";
import { io } from "socket.io-client";
import api from "@/utils/axios";
import { useInventoryStore } from "@/store/inventory";
import { usePlayerStore } from "@/store/player";
import { useToastStore } from "@/store/toast";

export const useShopStore = defineStore("shop", () => {
  const shopItems = ref([]);
  const wasUpdated = ref(false);
  const isConnected = ref(false);

  const toastStore = useToastStore();
  let socket = null;
  let listenersAttached = false;

  function connectSocket() {
    if (!import.meta.env.VITE_WS_URL) {
      console.error("❌ [SHOP] VITE_WS_URL не задан!");
      return;
    }

    if (socket && socket.connected) {
      console.log("🟡 [SHOP] Socket уже подключён.");
      return;
    }

    console.log("🔄 [SHOP] Подключаем Socket.IO к /shop...");
    socket = io(import.meta.env.VITE_WS_URL, {
      path: "/socket.io",
      transports: ["websocket"],
      withCredentials: true,
    });
    

    socket.on("connect", () => {
      socket.emit("join", null); // можно удалить, если не нужно
      console.log("✅ [SHOP] Socket.io подключён!");
    });

    socket.on("disconnect", () => {
      console.log("❌ [SHOP] Socket.io отключён.");
      isConnected.value = false;
    });

    if (!listenersAttached) {
      socket.on("shop_update", (data) => {
        console.log("📦 [SHOP] Обновление магазина:", data.products);
        shopItems.value = [...data.products.map(p => ({ ...p }))]
        wasUpdated.value = true;
        toastStore.addToast("Магазин обновился!", { type: "info" });
        setTimeout(() => (wasUpdated.value = false), 1000);
      });
      listenersAttached = true;
    }
  }

  function getCookie(name) {
    const match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
    return match ? match[2] : null;
  }

  const fetchShopItems = async (category) => {
    try {
      const url = category ? `/shop/?category=${category}` : `/shop`;
      const response = await api.get(url);
      shopItems.value = response.data.products;
    } catch (error) {
      console.error("Ошибка загрузки товаров:", error);
      toastStore.addToast("Ошибка загрузки товаров!", { type: "error" });
    }
  };

  const buyProduct = async (productId, productName, category) => {
    const csrfToken = getCookie("csrf_access_token");
    try {
      const response = await api.post(`/shop/buy/${productId}`, null, {
        withCredentials: true,
        headers: {
          "X-CSRF-TOKEN": csrfToken,
        },
      });

      const message = response.data?.message
        ? response.data.message
        : `Поздравляем с покупкой ${productName}!`;

      toastStore.addToast(message, { type: "success" });

      const inventoryStore = useInventoryStore();
      const playerStore = usePlayerStore();
      await inventoryStore.fetchInventory();
      await fetchShopItems(category);
      await playerStore.fetchPlayer();
    } catch (error) {
      console.error("Ошибка покупки товара:", error);
      toastStore.addToast("Не хватает денег!", { type: "error" });
    }
  };

  return {
    shopItems,
    wasUpdated,
    isConnected,
    fetchShopItems,
    buyProduct,
    connectSocket,
  };
});






