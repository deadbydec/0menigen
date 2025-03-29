import { io } from "socket.io-client";

const socket = io("https://localhost:5002", {
    transports: ["websocket", "polling"],
    secure: true,
    rejectUnauthorized: false,
});

socket.on("connect", () => {
    console.log("✅ Подключено к Socket.IO!");
});

socket.on("auth_success", (data) => {
    console.log("🔑 Авторизация успешна:", data);
});

socket.on("auth_failed", (data) => {
    console.error("❌ Ошибка авторизации:", data.error);
});

export default socket;
