import os
import uvicorn
import re
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

app = FastAPI()

# --- 核心意图重力场引擎 ---
class IntentEngine:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.suggested_intent = "正在感知重心..."
        self.locked_intent = "尚未锁定"
        self.is_confirmed = False

    async def get_reply(self, user_input, force_intent=None):
        if not self.client: return "【错误】未配置 API Key。"
        if force_intent:
            self.primary_intent = force_intent # 兼容旧逻辑变量名
            self.locked_intent = force_intent
            self.is_confirmed = True
            return f"SYSTEM_UPDATE|重心已手动重置为：{force_intent}"
        confirm_words = ["对", "是", "没错", "确认", "锁定", "这就是重心", "对的"]
        if not self.is_confirmed and user_input.strip() in confirm_words:
            if self.suggested_intent != "正在感知重心...":
                self.locked_intent = self.suggested_intent
                self.is_confirmed = True
                return f"CONFIRMED_SIGNAL|重心已对齐并锁死：{self.locked_intent}。"
        if not self.is_confirmed:
            system_prompt = "你是一个洞察力极强的军师。任务：从用户对话（生意、恋爱、合伙）中挖掘底层动机。回答顺耳自然。必须在末尾以 @@@关键词 结尾。"
        else:
            system_prompt = f"当前已锁定重心：{self.locked_intent}。执行 90% 权重策略，所有回答必须死扣这个重心。"
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
                temperature=0.4
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

# --- 压缩后的抗干扰 UI ---
HTML_PAGE = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><title>重心锚定系统</title><style>body{background:#0a0a0a;color:#e0e0e0;font-family:sans-serif;margin:0;display:flex;justify-content:center;padding:15px}.container{width:100%;max-width:850px;background:#141414;border-radius:12px;display:flex;flex-direction:column;height:95vh;border:1px solid #222;overflow:hidden}#status-bar{padding:15px 25px;background:#111;border-bottom:1px solid #222;display:flex;flex-direction:column;gap:10px}.status-line{display:flex;justify-content:space-between;align-items:center;height:30px}.label{color:#444;font-weight:bold;font-size:11px;width:120px;letter-spacing:1px}#suggest-box{color:#888;font-size:13px;flex:1;font-style:italic}#locked-box{color:#333;font-weight:bold;font-size:14px;flex:1}.active-lock{color:#27ae60!important}.btn-group{display:flex;gap:10px}.btn{font-size:10px;border:none;padding:5px 12px;border-radius:4px;cursor:pointer;font-weight:bold}.btn-ok{background:#1a1a1a;color:#27ae60;border:1px solid #27ae60}.btn-edit{background:#222;color:#666}#display{flex:1;overflow-y:auto;padding:30px}.row{margin-bottom:25px}.tag{font-size:10px;color:#333;margin-bottom:6px;font-weight:bold}.content{line-height:1.8;border-left:2px solid #222;padding-left:18px;color:#bbb;font-size:15px}.locked-line{border-left-color:#27ae60!important;color:#fff}.input-area{display:flex;padding:20px;background:#0d0d0d;border-top:1px solid #222;gap:15px}input{flex:1;background:#181818;border:1px solid #333;color:white;padding:12px;border-radius:6px;outline:none}button#send-btn{background:#222;color:white;border:1px solid #444;padding:0 30px;border-radius:6px;cursor:pointer}</style></head><body><div class="container"><div id="status-bar"><div class="status-line"><span class="label">📡 雷达实时推测:</span><span id="suggest-box">准备就绪...</span><button class="btn btn-ok" onclick="confirmIntent()">点击锁定</button></div><div class="status-line" style="border-top:1px solid #222;padding-top:10px"><span class="label">🎯 当前确认重心:</span><span id="locked-box">尚未锁定</span><button class="btn btn-edit" onclick="editIntent()">手动重置</button></div></div><div id="display"></div><div class="input-area"><input type="text" id="userInput" placeholder="随便聊聊..."><button id="send-btn" onclick="send()">发送</button></div></div><script>const display=document.getElementById('display'),suggestBox=document.getElementById('suggest-box'),lockedBox=document.getElementById('locked-box'),input=document.getElementById('userInput');let hasL=false,curL="";async function confirmIntent(){const res=await fetch(`/chat?q=锁定`);const data=await res.json();updateUI(data.reply)}async function editIntent(){const n=prompt("主公，请明示新的核心重心：");if(n){const res=await fetch(`/chat?force=${encodeURIComponent(n)}`);const data=await res.json();curL=n;updateUI(data.reply,true)}}function updateUI(reply,f=false){let isLocked=f,cR=reply;if(reply.startsWith("CONFIRMED_SIGNAL|")){cR=reply.split("|")[1];isLocked=true;curL=suggestBox.innerText}else if(reply.startsWith("SYSTEM_UPDATE|")){cR=reply.split("|")[1];isLocked=true}else if(reply.includes("|SUGGEST|")){const p=reply.split("|SUGGEST|");cR=p[0];suggestBox.innerText=p[1].trim()}if(isLocked||hasL){hasL=true;lockedBox.innerText=curL;lockedBox.classList.add('active-lock')}display.innerHTML+=`<div class="row"><div class="tag">AI COUNSELOR</div><div class="content ${hasL?'locked-line':''}">${cR.replace(/\\n/g,'<br>')}</div></div>`;display.scrollTop=display.scrollHeight}async function send(){const v=input.value.trim();if(!v)return;display.innerHTML+=`<div class="row"><div class="tag">USER</div><div class="content">${v}</div></div>`;input.value='';const res=await fetch(`/chat?q=${encodeURIComponent(v)}`);const data=await res.json();updateUI(data.reply)}input.onkeypress=(e)=>{if(e.key==='Enter')send()}</script></body></html>"""

@app.get("/", response_class=HTMLResponse)
async def home(): return HTML_PAGE

@app.get("/chat")
async def chat(q: str = None, force: str = None):
    if force: reply = await engine.get_reply("", force_intent=force)
    else: reply = await engine.get_reply(q)
    return JSONResponse({"reply": reply})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)