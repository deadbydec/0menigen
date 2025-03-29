from fastapi import FastAPI
from routes import auth_router, chat_router, shop_router, news_router, index_router, player_router, players_router, inventory_router, games_router, profile_router, friends_router, messages_router, wall_router, achievements_router, leaderboard_router, forum_router

app = FastAPI()

# Подключаем все роутеры так же, как в main.py:
app.include_router(index_router)
app.include_router(players_router)
app.include_router(auth_router, prefix="/api/auth")
app.include_router(news_router, prefix="/api/news")
app.include_router(chat_router, prefix="/api/chat")
app.include_router(shop_router, prefix="/api/shop")
app.include_router(inventory_router, prefix="/api/inventory")
app.include_router(forum_router, prefix="/api/forum")
app.include_router(games_router, prefix="/api/games")
app.include_router(profile_router, prefix="/api/profile")
app.include_router(friends_router, prefix="/api/friends")
app.include_router(messages_router, prefix="/api/messages")
app.include_router(wall_router, prefix="/api/wall")
app.include_router(achievements_router, prefix="/api/achievements")
app.include_router(leaderboard_router, prefix="/api/leaderboard")
app.include_router(player_router)  # ВАЖНО: без лишнего prefix!

print("🛣️ Зарегистрированные маршруты в FastAPI:\n")

for route in app.routes:
    path = getattr(route, "path", None)
    methods = getattr(route, "methods", None)
    endpoint = getattr(route, "endpoint", None)

    if path and methods:
        method_list = ", ".join(methods)
        endpoint_name = getattr(endpoint, "__name__", "-")
        print(f"[{method_list}] {path} → {endpoint_name}")
    else:
        print(f"[MOUNTED] {getattr(route, 'name', '-')} → {getattr(route, 'app', type(route.app))}")


