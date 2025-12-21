import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

app = FastAPI()

class IntentEngine:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.suggested_intent = "扫描中..."
        self.locked_intent = "尚未锁定"
        self.is_confirmed = False

    async def get_reply(self, user_input, force_intent=None):
        if not self.client: return "【错误】未配置 API Key。"

        # 1. 重心切换逻辑
        if force_intent:
            self.locked_intent = force_intent
            self.is_confirmed = True
            return f"SYSTEM_UPDATE|重心已重置为：{force_intent}"

        confirm_words = ["对", "是", "没错", "确认", "锁定", "换吧", "好", "对的"]
        if user_input.strip() in confirm_words:
            self.locked_intent = self.suggested_intent
            self.is_confirmed = True
            return f"CONFIRMED_SIGNAL|重心已对齐：{self.locked_intent}。"

        # 2. 构造 Prompt：死守重心 vs 侧翼扫描
        if not self.is_confirmed:
            system_prompt = (
                "你是一个冷峻的军师。当前为【追踪期】。任务：挖掘用户底层动机。\n"
                "必须在末尾另起一行输出 '@@@简短关键词'。"
            )
        else:
            system_prompt = (
                f"你目前的【核心重心】是：{self.locked_intent}。\n"
                "【执行原则】：\n"
                "1. 必须以 90% 的权重围绕核心重心深度拆解。\n"
                "2. 若用户话题明显偏离，请在回复末尾简单应对，并询问：'发现话题变了，是否需要切换重心？'\n"
                "3. 严禁强行融合话题。必须在末尾另起一行输出 '@@@最新潜在意图'。"
            )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
                temperature=0.3
            )
            raw_reply = response.choices[0].message.content
            
            if "@@@" in raw_reply:
                parts = raw_reply.split("@@@")
                clean_text = parts[0].strip()
                self.suggested_intent = parts[1].strip()
                return f"{clean_text} |SUGGEST| {self.suggested_intent}"
            return raw_reply
        except Exception as e:
            return f"【异常】连接失败：{str(e)}"

engine = IntentEngine()

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/chat")
async def chat(q: str = None, force: str = None):
    if force: reply = await engine.get_reply("", force_intent=force)
    else: reply = await engine.get_reply(q)
    return JSONResponse({"reply": reply})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)