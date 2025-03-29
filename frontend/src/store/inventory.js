// inventory.js
import { defineStore } from "pinia";
import { ref, onMounted, onUnmounted } from "vue";
import api from "@/utils/axios";

export const useInventoryStore = defineStore("inventory", () => {
  const inventory = ref([]);
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
      inventory.value = response.data.inventory || []
    } catch (error) {
      console.error("Ошибка загрузки инвентаря:", error);
    }
  };

  // Использование предмета: вызываем API, затем fetchInventory() для гарантии актуальности
  const useItem = async () => {
    if (!selectedItem.value) {
      alert("Выберите предмет перед использованием!");
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
      alert(response.data.message);
      await fetchInventory(); // подтягиваем актуальные данные из базы
      selectedItem.value = null;
    } catch (error) {
      console.error("Ошибка использования предмета:", error);
    }
  };

  // Уничтожение предмета: то же самое — API и затем fetchInventory()
  const destroyItem = async () => {
    if (!selectedItem.value) {
      alert("Выберите предмет перед удалением!");
      return;
    }
    try {
      const response = await api.delete(
        `/inventory/destroy/${selectedItem.value.id}`,
        {
          withCredentials: true,
          headers: { "X-CSRF-TOKEN": csrfToken }
        }
      );
      alert(response.data.message);
      selectedItem.value = null;
      await fetchInventory();
    } catch (error) {
      console.error("Ошибка уничтожения предмета:", error);
    }
  };

  // Выбор предмета
  const selectItem = (item) => {
    selectedItem.value = selectedItem.value?.id === item.id ? null : item;
  };

  // При монтировании компонента сразу загружаем инвентарь


  return {
    inventory,
    selectedItem,
    fetchInventory,
    useItem,
    destroyItem,
    selectItem
  };
});

