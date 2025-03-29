import { createApp } from "vue";
import { createPinia } from "pinia";
import { useAuthStore } from "@/store/auth";
import { io } from "socket.io-client";
import App from "./App.vue";
import router from "./router";
import axios from "./utils/axios"; // ✅ Теперь axios уже настроен на куки
import "font-awesome/css/font-awesome.min.css";
import { fas } from "@fortawesome/free-solid-svg-icons";
import { library } from "@fortawesome/fontawesome-svg-core";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import FloatingVue from 'floating-vue'
import 'floating-vue/dist/style.css'

const app = createApp(App);

const pinia = createPinia();
app.use(pinia);

const authStore = useAuthStore();
await authStore.fetchUser();

const API_URL = import.meta.env.VITE_API_URL || "https://localhost:5002";
const socket = io(import.meta.env.VITE_WS_URL, {
  transports: ["websocket"],
  withCredentials: true,
  rejectUnauthorized: false, // Если нужно отключить проверку сертификата
});

app.config.globalProperties.$axios = axios;
app.config.globalProperties.$socket = socket;
app.component("font-awesome-icon", FontAwesomeIcon);
app.use(router);
app.provide("socket", socket);
library.add(fas); 
app.use(FloatingVue)

app.mount("#app");

console.log("📌 import.meta.env:", import.meta.env);
console.log("📌 API URL:", API_URL);


