# src/modules/reddit_manager.py
import os
import urllib.parse
import praw

# Scopes valides (adapte si besoin)
SCOPES = ["identity", "read", "submit", "mysubreddits"]
REDIRECT_URI = os.getenv("WEBHOOK_URL", "https://mostly.pages.dev/copy-code/")

def _build_auth_url(client_id: str, state: str) -> str:
    params = {
        "client_id": client_id,
        "response_type": "code",
        "state": state,
        "redirect_uri": REDIRECT_URI,
        "duration": "permanent",
        "scope": " ".join(SCOPES),
    }
    return "https://www.reddit.com/api/v1/authorize?" + urllib.parse.urlencode(params)

class RedditManager:
    @staticmethod
    def create_auth_url(user_id: int, client_id: str, client_secret: str) -> str:
        # state peut être user_id ou un uuid
        state = str(user_id)
        return _build_auth_url(client_id, state)

    @staticmethod
    def authorize_user(user_id: int, code: str, client_id: str, client_secret: str):
        # IMPORTANT : même redirect_uri que plus haut
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=REDIRECT_URI,
            user_agent=os.getenv("REDDIT_USER_AGENT", "tele2reddit/1.0"),
        )
        refresh_token = reddit.auth.authorize(code)  # échange code -> token
        me = reddit.user.me()
        return refresh_token, str(me.name)
