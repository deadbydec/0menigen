// store/shop.js

import { defineStore } from "pinia";
import { ref } from "vue";
import { io } from "socket.io-client";
import api from "@/utils/axios";
import { useInventoryStore } from "@/store/inventory";
import { usePlayerStore } from "@/store/player";
import { useToastStore } from '@/store/toast' // 👈 импорт сторов как обычно

export const useShopStore = defineStore("shop", () => {
  const shopItems = ref([]);
  const wasUpdated = ref(false);
  const toastStore = useToastStore()

  const socket = io(import.meta.env.VITE_WS_URL + "/shop", {
    transports: ["websocket"],
    withCredentials: true,
    rejectUnauthorized: false,
  });

  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : null;
  }

  const fetchShopItems = async (category) => {
    try {
      const response = await api.get(`/shop/?category=${category}`);
      shopItems.value = response.data.products;
    } catch (error) {
      console.error("Ошибка загрузки товаров:", error);
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
      console.log("Покупка успешно завершена:", response.data);
    // Если API не вернул productName, используем тот, что передали
    const message =
      response.data && response.data.message
        ? response.data.message
        : `Поздравляем с покупкой ${productName}!`;
        toastStore.addToast(message, { type: 'success' });
      

      const inventoryStore = useInventoryStore();
      const playerStore = usePlayerStore();

      await inventoryStore.fetchInventory();
      await fetchShopItems(category);
      await playerStore.fetchPlayer();
    } catch (error) {
      console.error("Ошибка покупки товара:", error);
      toastStore.addToast("Не хватает денег!", { type: 'error' });
    }
  };

  // 🔄 Автообновление по сокету
  socket.on("shop_update", (data) => {
    console.log("🔄 Магазин обновился!", data.products);
    shopItems.value.splice(0, shopItems.value.length, ...data.products);
    wasUpdated.value = true;
    toast.info("Магазин обновился!");
    setTimeout(() => (wasUpdated.value = false), 1000);
  });

  return {
    shopItems,
    fetchShopItems,
    buyProduct,
    wasUpdated,
  };
});



