// inventory.js
import { defineStore } from "pinia";
import { ref, onMounted, onUnmounted } from "vue";
import api from "@/utils/axios";
import { useToastStore } from '@/store/toast' // 👈 импорт сторов как обычно

export const useInventoryStore = defineStore("inventory", () => {
  const inventory = ref([]);
  const toastStore = useToastStore()
  const userRace = ref(""); // Новое поле для расы пользователя
  const selectedItem = ref(null);
  const csrfToken = getCookie("csrf_access_token");

  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : null;
  }

  // Загружаем инвентарь из базы — как банковский счёт, который всегда достоверен
  const fetchInventory = async () => {
    try {
      const response = await api.get("/inventory/", {
        withCredentials: true,
        headers: { "Cache-Control": "no-cache", "Pragma": "no-cache" }
      });
      inventory.value = (response.data.inventory || []).filter(item => item.quantity > 0);
      userRace.value = response.data.user_race || ""; // Сохраняем расу пользователя
    } catch (error) {
      console.error("Ошибка загрузки инвентаря:", error);
      toastStore.addToast("Ошибка загрузки инвентаря", { type: 'error' });
    }
  };

  // Использование предмета: вызываем API, затем fetchInventory() для гарантии актуальности
  const useItem = async () => {
    if (!selectedItem.value) {
      toast.error("Выберите предмет перед использованием!");
      return;
    }
    try {
      const response = await api.post(
        `/inventory/use/${selectedItem.value.id}`,
        null,
        {
          withCredentials: true,
          headers: { "X-CSRF-TOKEN": csrfToken }
        }
      );
      toastStore.addToast(response.data.message, { type: 'success' });
      await fetchInventory(); // подтягиваем актуальные данные из базы
      selectedItem.value = null;
    } catch (error) {
      console.error("Ошибка использования предмета:", error);
      toastStore.addToast("Блять. Я не могу это использовать!", { type: 'error' });
    }
  };

  // Уничтожение предмета: то же самое — API и затем fetchInventory()
  const destroyItem = async () => {
    if (!selectedItem.value) {
      toast.error("Выберите предмет перед удалением!");
      return;
    }
    try {
      const response = await api.delete(
        `/inventory/discard/${selectedItem.value.id}`,
        {
          withCredentials: true,
          headers: { "X-CSRF-TOKEN": csrfToken }
        }
      );
      toastStore.addToast(response.data.message, { type: 'success' });
      selectedItem.value = null;
      await fetchInventory();
    } catch (error) {
      console.error("Ошибка уничтожения предмета:", error);
      toast.error("Ошибка при выбрасовании предмета!");
    }
  };

  const recycleItem = async () => {
    if (!selectedItem.value) return alert("Выберите предмет для переработки!");
    try {
      const response = await api.post(
        `/inventory/recycle/${selectedItem.value.id}`,
        null,
        {
          withCredentials: true,
          headers: { "X-CSRF-TOKEN": csrfToken }
        }
      );
      toastStore.addToast(response.data.message, { type: 'success' });
      await fetchInventory();
      selectedItem.value = null;
    } catch (error) {
      console.error("Ошибка переработки предмета:", error);
      toastStore.addToast("Сука! Я не могу это переработать!", { type: 'error' });
    }
  };

  const sendToVault = async (itemId, quantity = 1) => {
    try {
      const payload = {
        item_id: itemId,
        quantity: quantity
      };
  
      const res = await api.post('/safe/vault/deposit-item', payload, {
        withCredentials: true,
        headers: { "X-CSRF-TOKEN": csrfToken }
      });
  
      toastStore.addToast(res.data.message, { type: 'success' });
      await fetchInventory();
      selectedItem.value = null;
      return res.data;
  
    } catch (error) {
      console.error("Ошибка при перемещении в сейф:", error);
      const msg = error.response?.data?.detail || "Ошибка: не удалось убрать предмет в сейф.";
      toastStore.addToast(msg, { type: 'error' });
      throw error;
    }
  };
  
  
  
  


  // Выбор предмета
  const selectItem = (item) => {
    selectedItem.value = selectedItem.value?.id === item.id ? null : item;
  };

  // При монтировании компонента сразу загружаем инвентарь


  return {
    inventory,
    userRace,
    selectedItem,
    fetchInventory,
    useItem,
    recycleItem,
    sendToVault,
    destroyItem,
    selectItem
  };
});

