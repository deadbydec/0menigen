import { ref } from "vue";
import { io } from "socket.io-client";
import axios from "axios";

const shopItems = ref([]);
const socket = io(import.meta.env.VITE_WS_URL + "/shop", {
  transports: ["websocket"],
  withCredentials: true,
  rejectUnauthorized: false, // если нужно для локального TLS
}); // Подключение к сокетам (живёт всегда)
const csrfToken = getCookie("csrf_access_token");

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : null;
  }  

const fetchShopItems = async (category) => {
  try {
    const response = await axios.get(`/api/shop/?category=${category}`);
    shopItems.value = response.data.products;
  } catch (error) {
    console.error("Ошибка загрузки товаров:", error);
  }
};

// Функция покупки товара
const buyProduct = async (productId) => {
    try {
      const response = await axios.post(`/api/shop/buy/${productId}`, null, { 
        withCredentials: true,
        headers: {
            "X-CSRF-TOKEN": csrfToken,
        }
     });
      console.log("Покупка успешно завершена:", response.data);
      // После покупки можно обновить магазин:
      // Например, если у тебя сохранена текущая категория, можно вызвать fetchShopItems(category)
      // fetchShopItems(currentCategory);
      await fetchInventory();
      await fetchShopItems(currentCategory);
      await fetchPlayer();
    } catch (error) {
      console.error("Ошибка покупки товара:", error);
    }
  };

// Подписка на обновления через сокеты (автоматически работает всегда)
socket.on("shop_update", (data) => {
  console.log("🔄 Магазин обновился!", data.products);
  shopItems.value = data.products;
});

export function useShopStore() {
  return { shopItems, fetchShopItems, buyProduct };
}

