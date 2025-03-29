from .index import router as index_router
from .news import router as news_router
from .auth import router as auth_router
from .profile import router as profile_router
from .chat import router as chat_router
from .shop import router as shop_router
from .forum import router as forum_router
from .inventory import router as inventory_router
from .games import router as games_router
from .inbox import router as inbox_router
from .wall import router as wall_router
from .friends import router as friends_router
from .players import router as players_router
from .achievements import router as achievements_router
from .leaderboard import router as leaderboard_router
from .player import router as player_router
from .gift import router as gift_router
from .toilet_doom import router as toilet_doom_router
from .admin import router as admin_router
from .dev_loader import router as dev_router

__all__ = [
    "dev_router",
    "admin_router",
    "toilet_doom_router",
    "gift_router",
    "index_router",
    "player_router",
    "leaderboard_router",
    "players_router",
    "achievements_router",
    "news_router",
    "auth_router",
    "profile_router",
    "chat_router",
    "shop_router",
    "forum_router",
    "inventory_router",
    "games_router",
    "inbox_router",
    "wall_router",
    "friends_router",
]
