import os
import json
from typing import Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# 1. 定义数据契约
class AnalyzeRequest(BaseModel):
    text: str
    env_power: int = 4

# 2. 核心推演逻辑 (林青霞协议)
def run_tao_logic(text: str, power: int):
    # 从系统环境变量读取 Key，保护安全
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        return "【警告】未检测到环境变量 OPENAI_API_KEY。当前处于离线模式，无法连接大脑。"

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # 逻辑分档
        mode = "【饱和变轨/萧何破壁】" if power >= 6 else "【低光核对/精密采样】"
        
        response = client.chat.completions.create(
            model="gpt-4o", # 或者使用 gpt-3.5-turbo
            messages=[
                {"role": "system", "content": f"你是一个名为‘林青霞协议’的极值逻辑引擎。风格：冷峻、手术刀般精准。当前模式：{mode}"},
                {"role": "user", "content": f"环境力等级：{power}/7。当前博弈采样：{text}。请给出极值推演结果。"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"链路阻断: {str(e)}"

# 3. 仪表盘页面 (HTML)
@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TAO Logic Console</title>
        <style>
            body { background: #0d1117; color: #58a6ff; font-family: sans-serif; display: flex; justify-content: center; padding-top: 50px; }
            .box { background: #161b22; border: 1px solid #30363d; padding: 25px; border-radius: 10px; width: 600px; box-shadow: 0 8px 32px rgba(0,0,0,0.5); }
            textarea { width: 100%; height: 120px; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 10px; border-radius: 6px; box-sizing: border-box; margin-bottom: 15px; }
            .row { display: flex; justify-content: space-between; margin-bottom: 20px; align-items: center; }
            input[type=range] { width: 60%; cursor: pointer; }
            button { background: #238636; color: white; border: none; padding: 12px; border-radius: 6px; width: 100%; cursor: pointer; font-weight: bold; font-size: 16px; }
            button:hover { background: #2ea043; }
            #res { margin-top: 20px; padding: 15px; background: #010409; border-left: 4px solid #58a6ff; color: #d1d5db; white-space: pre-wrap; line-height: 1.6; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2 style="color: #f0f6fc; margin-top:0;">TAO-Engine 控制台 v1.5</h2>
            <textarea id="txt" placeholder="在此输入博弈采样文本..."></textarea>
            <div class="row">
                <span>环境力档位: <b id="pv">4</b> / 7</span>
                <input type="range" id="p" min="1" max="7" value="4" oninput="document.getElementById('pv').innerText=this.value">
            </div>
            <button onclick="go()">点火运行 (Execute)</button>
            <div id="res">等待指令...</div>
        </div>
        <script>
            async function go() {
                const resDiv = document.getElementById('res');
                resDiv.innerText = "正在通过林青霞协议进行极值推演...";
                const r = await fetch('/api/v1/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: document.getElementById('txt').value, env_power: parseInt(document.getElementById('p').value)})
                });
                const d = await r.json();
                resDiv.innerText = d.reply;
            }
        </script>
    </body>
    </html>
    """

# 4. API 路由
@app.post("/api/v1/run")
async def run_api(req: AnalyzeRequest):
    reply = run_tao_logic(req.text, req.env_power)
    return {"ok": True, "reply": reply}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)