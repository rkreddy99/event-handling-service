from tornado.web import HTTPError
from config import API_TOKEN

def authenticate(handler):
    def wrapper(self, *args, **kwargs):
        auth_header = self.request.headers.get("Authorization", "")
        #print(API_TOKEN)
        if not auth_header.startswith("Bearer ") or auth_header.split(" ")[1] != API_TOKEN:
            raise HTTPError(401, "Unauthorized")
        return handler(self, *args, **kwargs)
    return wrapper

