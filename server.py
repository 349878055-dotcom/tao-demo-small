import os
import random
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from openai import OpenAI  # 需要安装这个库：pip install openai

app = FastAPI()

# --- 核心逻辑引擎：联网版 ---
class LogicHunter:
    def __init__(self):
        # 从环境变量读取 API Key，这样最安全
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.ai_restart_lock = False

    async def process(self, context, imbalance, security):
        if imbalance < 0.6: return "（状态自洽，系统静默中...）"

        # 如果没有配置 Key，就退回到原来的随机比喻模式
        if not self.client:
            return "【系统提示】未检测到大脑连接，请在 Render 后台配置 OPENAI_API_KEY。"

        # 构造给 ChatGPT 的指令 (Prompt)
        system_prompt = (
            "你是一个名为‘幻象拆解师’的逻辑专家，外号‘平头哥’。你的核心立场是：反PUA、反伪道德、解构虚伪权威。"
            "语气要求：极度辛辣、多用比喻、调侃、幽默，但对失衡者要提供具体的逻辑托底。"
            "输出格式：【拆解】一段话（辛辣警醒） \n\n 【支撑】一段话（具体的逻辑路径，不准说废话）"
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo", # 或者 gpt-4
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"【拆解】大脑连接超时... \n\n 【支撑】检查你的 API Key 是否有效或网络是否通畅。"

hunter = LogicHunter()

# --- 网页界面代码 (保持不变) ---
HTML_CONTENT = """...(和你之前的HTML一样)..."""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_CONTENT

@app.get("/chat")
async def chat(q: str):
    ans = await hunter.process(q, 0.85, 0.8)
    return {"ans": ans}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000) # Render 要求监听 10000 端口

    @app.get("/chat")
    async def chat(q: str):
    # 这里我们把网页上的滑块数值默认传进去（或者你可以根据需要扩展参数）
     ans = await hunter.process(q, 0.85, 0.8) 
     return {"reply": ans}