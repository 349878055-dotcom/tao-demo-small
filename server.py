import os
import uvicorn
import re
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

app = FastAPI()

# --- 核心意图引擎 (Logic Engine) ---
class IntentEngine:
    def __init__(self):
        # 自动读取环境变量中的 API KEY
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.primary_intent = "尚未捕捉"
        self.is_confirmed = False

    async def get_reply(self, user_input):
        if not self.client:
            return "【错误】后台未检测到 OpenAI API Key。"

        # 1. 检测双向确认信号
        confirm_words = ["对", "是", "没错", "确认", "就是这个", "对的", "正确"]
        if not self.is_confirmed and any(word == user_input.strip() for word in confirm_words):
            if self.primary_intent != "尚未捕捉":
                self.is_confirmed = True
                return f"【系统指令】重心已锁定：{self.primary_intent}。现在进入 90% 权重深度对焦模式。请继续。"

        # 2. 根据状态配置 Prompt
        if not self.is_confirmed:
            # 瞎聊/雷达追踪期
            system_prompt = (
                "你是一个具有深度洞察力的军师，目前处于【意图追踪期】。"
                "任务：从用户瞎聊的内容中提取核心利益点。语气要顺耳、随和。"
                "要求：每句话最后必须另起一行，以'【意图感知】：(你捕捉到的重心)'结尾。"
            )
        else:
            # 锁定/90%权重爆发期
            system_prompt = (
                f"当前主要意图已锁定为：{self.primary_intent}。"
                "现在执行 90% 权重策略：无论用户说什么，你都要强行拉回到该重心进行深度解析。"
                "你要像老江湖一样，用对方的废话当引子，引出主要矛盾。语气：忠言顺耳。"
            )

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.5
            )
            reply = response.choices[0].message.content

            # 3. 如果没锁定，更新雷达扫描到的意图
            if not self.is_confirmed:
                match = re.search(r"【意图感知】：(.*)", reply)
                if match:
                    self.primary_intent = match.group(1).strip()

            return reply
        except Exception as e:
            return f"【异常】无法连接大脑：{str(e)}"

engine = IntentEngine()

# --- 极简 Google 风格前端 (Google UI) ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>意图追踪引擎</title>
    <style>
        :root { --bg: #121212; --panel: #1e1e1e; --green: #27ae60; --gray: #333; --text: #e0e0e0; }
        body { background: var(--bg); color: var(--text); font-family: 'Roboto', sans-serif; display: flex; justify-content: center; padding: 20px; margin: 0; }
        .container { width: 100%; max-width: 700px; background: var(--panel); border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); display: flex; flex-direction: column; height: 90vh; }
        
        /* 亮灯窗口 */
        #status-bar { padding: 15px; text-align: center; background: var(--gray); font-size: 14px; transition: 0.5s; border-radius: 8px 8px 0 0; color: #aaa; border-bottom: 1px solid #444; }
        .confirmed { background: var(--green) !important; color: white !important; font-weight: bold; }

        /* 聊天显示区 */
        #display { flex: 1; overflow-y: auto; padding: 20px; border-bottom: 1px solid #444; scroll-behavior: smooth; }
        .chat-row { margin-bottom: 20px; padding: 10px; border-radius: 4px; transition: background 0.3s; }
        .chat-row:hover { background: rgba(255,255,255,0.02); }
        .user-tag { color: #7f8c8d; font-size: 12px; margin-bottom: 5px; text-transform: uppercase; }
        .ai-content { line-height: 1.7; white-space: pre-wrap; word-wrap: break-word; border-left: 2px solid #444; padding-left: 15px; }
        .locked-border { border-left-color: var(--green) !important; }

        /* 输入区 */
        .input-box { display: flex; padding: 15px; gap: 10px; }
        input { flex: 1; background: #2c2c2c; border: 1px solid #444; color: white; padding: 12px; border-radius: 4px; outline: none; }
        button { background: #444; color: white; border: none; padding: 0 20px; border-radius: 4px; cursor: pointer; transition: 0.3s; }
        button:hover { background: var(--green); }
    </style>
</head>
<body>
    <div class="container">
        <div id="status-bar">🔍 正在实时追踪意图...</div>
        <div id="display"></div>
        <div class="input-box">
            <input type="text" id="userInput" placeholder="随便聊聊，输入'对'锁定重心...">
            <button onclick="send()">发送</button>
        </div>
    </div>

    <script>
        const status = document.getElementById('status-bar');
        const display = document.getElementById('display');
        const input = document.getElementById('userInput');

        async function send() {
            const text = input.value.strip ? input.value.trim() : input.value;
            if(!text) return;

            display.innerHTML += `<div class="chat-row"><div class="user-tag">USER</div><div>${text}</div></div>`;
            input.value = '';
            display.scrollTop = display.scrollHeight;

            const res = await fetch(`/chat?q=${encodeURIComponent(text)}`);
            const data = await res.json();
            const reply = data.reply;

            // 亮灯逻辑
            let borderClass = "";
            if(reply.includes("重心已锁定") || reply.includes("执行 90% 权重")) {
                status.classList.add('confirmed');
                status.innerText = "✅ 重心已对焦：90% 权重执行中";
                borderClass = "locked-border";
            } else if(reply.includes("【意图感知】：")) {
                const found = reply.split("【意图感知】：")[1];
                status.innerText = "💡 捕捉到重心：" + found.split('\\n')[0] + " (输入'对'锁定)";
            }

            display.innerHTML += `
                <div class="chat-row">
                    <div class="user-tag">AI COUNSELOR</div>
                    <div class="ai-content ${borderClass}">${reply}</div>
                </div>`;
            display.scrollTop = display.scrollHeight;
        }

        input.onkeypress = (e) => { if(e.key === 'Enter') send(); };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE

@app.get("/chat")
async def chat(q: str):
    reply = await engine.get_reply(q)
    return JSONResponse({"reply": reply})

if __name__ == "__main__":
    # 提示：运行后访问 http://127.0.0.1:8000
    uvicorn.run(app, host="127.0.0.1", port=8000)