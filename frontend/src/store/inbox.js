// src/store/inbox.js
import { defineStore } from "pinia";
import { ref } from "vue";
import api from "@/utils/axios";

export const useInboxStore = defineStore("inbox", () => {
  const inboxMessages = ref([]);
  const sentMessages = ref([]);
  const isModalOpen = ref(false); // Контроль модального окна
  const currentTab = ref("inbox"); // ✅ Добавляем текущую вкладку в стор
  


  
  // 🔥 Загружаем входящие сообщения
  const fetchInbox = async () => {
    try {
      const response = await api.get("/inbox/");
      inboxMessages.value = response.data || [];
    } catch (error) {
      console.error("Ошибка загрузки входящих:", error);
    }
  };

  // 🔥 Загружаем исходящие сообщения
  const fetchSent = async () => {
    try {
      const response = await api.get("/inbox/sent");
      sentMessages.value = response.data || [];
    } catch (error) {
      console.error("Ошибка загрузки исходящих:", error);
    }
  };

  const sendMessage = async ({ recipient, content, subject }) => {
    try {
      const response = await api.post("/inbox/send", {
        recipient,
        content,
        subject,
      }, {
        withCredentials: true
      });
      if (response.data.success) {
        fetchSent();
      }
      return response.data;
    } catch (error) {
      console.error("Ошибка отправки сообщения:", error);
      return { error: "Не удалось отправить сообщение." };
    }
  };
  

  // 🔥 Удаление сообщения
  const deleteMessage = async (messageId) => {
    try {
      await api.delete(`/inbox/delete/${messageId}`);
      fetchInbox();
      fetchSent();
    } catch (error) {
      console.error("Ошибка удаления:", error);
    }
  };

  async function acceptGift(giftId) {
    try {
      const response = await api.post(`/gift/accept/${giftId}`)
  
      if (response.data?.success) {
        alert("Подарок принят!")
        inboxStore.fetchInbox() // обновим почту
      } else {
        // 🎯 Сервер вернул ответ, но без success=true
        alert(response.data.message || "Что-то пошло не так при принятии подарка")
      }
  
    } catch (err) {
      console.error("Ошибка при принятии подарка", err)
      alert("Ошибка принятия подарка") // сюда попадут только критичные ошибки (403, 500 и т.п.)
    }
  }
  
  
  async function rejectGift(giftId) {
    try {
      await api.post(`/gift/reject/${giftId}`)
      alert("Подарок отклонён.")
      inboxStore.fetchInbox()
    } catch (err) {
      console.error("Ошибка при отклонении подарка", err)
      alert("Ошибка отклонения подарка")
    }
  }


// В твоем inboxStore или в компоненте
function clearEmptyMessages() {
  inboxStore.inboxMessages = inboxStore.inboxMessages.filter(msg => msg.id)
}
  

  // 🔥 Открытие модального окна и сброс вкладки на "Входящие"
  const openModal = () => {
    isModalOpen.value = true;
    currentTab.value = "inbox"; // ✅ Теперь вкладка всегда сбрасывается на "Входящие"
    fetchInbox();
    fetchSent();
  };

  const closeModal = () => {
    isModalOpen.value = false;
  };

  return {
    rejectGift,
    acceptGift,
    inboxMessages,
    sentMessages,
    fetchInbox,
    fetchSent,
    sendMessage,
    deleteMessage,
    isModalOpen,
    currentTab,
    openModal,
    closeModal,
    clearEmptyMessages,
  };
});
