import os
import random
import uvicorn
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from openai import OpenAI

app = FastAPI()

# --- 核心逻辑引擎 ---
class LogicHunter:
    def __init__(self):
        # 自动从 Render 后台读取你的 OPENAI_API_KEY
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    async def process(self, context):
        if not self.client:
            return "【错误】未在后台检测到 API Key，请检查配置。"

        system_prompt = (
            "你是一个名为‘幻象拆解师’的专家，外号‘平头哥’。你的核心立场是：反PUA、反伪道德、解构虚伪权威。"
            "语气要求：极度辛辣、多用比喻、调侃，但要提供具体的逻辑支撑。"
            "输出格式：【拆解】一段话 \n\n 【支撑】一段话"
        )

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"【错误】大脑连接超时，可能是 Key 无效。错误详情：{str(e)}"

hunter = LogicHunter()

# --- 这里是焊死的 HTML 界面，确保万无一失 ---
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>幻象拆解师</title>
    <style>
        body { background:#1a1a1a; color:#ecf0f1; font-family:sans-serif; display:flex; justify-content:center; padding-top:50px; margin:0; }
        .terminal { width:90%; max-width:500px; background:#2c3e50; border-radius:12px; border-top:4px solid #e74c3c; overflow:hidden; }
        .header { background:#000; padding:20px; text-align:center; }
        .display { height:350px; padding:20px; overflow-y:auto; background:#111; line-height:1.6; }
        .input-area { display:flex; padding:15px; background:#222; gap:10px; }
        input { flex:1; background:#333; border:1px solid #555; color:#fff; padding:10px; border-radius:6px; }
        button { background:#e74c3c; color:#fff; border:none; padding:0 20px; border-radius:6px; cursor:pointer; font-weight:bold; }
        .red { color:#e74c3c; font-weight:bold; }
        .green { color:#27ae60; }
    </style>
</head>
<body>
<div class="terminal">
    <div class="header">
        <div style="font-size:40px">🦡</div>
        <div style="font-size:1.2rem;font-weight:bold;margin-top:10px">幻象拆解师</div>
    </div>
    <div id="chatDisplay" class="display">系统已就绪，请输入那些让你怀疑人生的虚假逻辑。</div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="例如：老板说大家都是一家人...">
        <button onclick="send()">拆解</button>
    </div>
</div>
<script>
    async function send() {
        const inp = document.getElementById('userInput');
        const disp = document.getElementById('chatDisplay');
        if(!inp.value) return;
        disp.innerHTML += `<div style="color:#7f8c8d;margin-top:10px;">> 正在拆解...</div>`;
        try {
            const resp = await fetch('/chat?q=' + encodeURIComponent(inp.value));
            const data = await resp.json();
            let text = data.reply.replace(/【拆解】/g, '<span class="red">【拆解】</span>').replace(/【支撑】/g, '<span class="green">【支撑】</span>');
            disp.innerHTML += `<div style="margin-top:15px;border-top:1px solid #333;padding-top:10px;">${text}</div>`;
        } catch(e) {
            disp.innerHTML += `<div style="color:orange;margin-top:10px;">[错误] 无法连接后端。</div>`;
        }
        disp.scrollTop = disp.scrollHeight;
        inp.value = '';
    }
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_CONTENT

@app.get("/chat")
async def chat(q: str):
    ans = await hunter.process(q)
    return {"reply": ans}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)