from fastapi      import FastAPI, HTTPException
from urllib.parse import urlparse, ParseResult
from pydantic     import BaseModel
from pathlib      import Path
from wrapper      import ChatGPT
from uvicorn      import run


app = FastAPI()

proxy_pool: list = []
proxy_file = Path("proxies.txt")
if proxy_file.exists():
    proxy_pool = [line.strip() for line in proxy_file.read_text().splitlines() if line.strip()]

class ConversationRequest(BaseModel):
    proxy: str = None
    message: str
    image: str = None
    search: bool = False

def format_proxy(proxy: str) -> str:

    if not proxy.startswith(("http://", "https://")):
        proxy: str = "http://" + proxy

    try:
        parsed: ParseResult = urlparse(proxy)

        if parsed.scheme not in ("http", ""):
            raise ValueError("Not http scheme")

        if not parsed.hostname or not parsed.port:
            raise ValueError("No url and port")

        if parsed.username and parsed.password:
            return f"http://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}"

        else:
            return f"http://{parsed.hostname}:{parsed.port}"

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid proxy format: {str(e)}")

@app.post("/conversation")
async def create_conversation(request: ConversationRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")

    try:
        if request.proxy:
            client = ChatGPT(proxy=format_proxy(request.proxy))
        elif proxy_pool:
            client = ChatGPT(proxy_pool=proxy_pool)
        else:
            client = ChatGPT()

        answer: str = client.ask_question(request.message, request.image, search=request.search)

        return {
            "status": "success",
            "result": answer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    run(app, host="0.0.0.0", port=6969)