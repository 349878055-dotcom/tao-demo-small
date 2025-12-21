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
        self.suggested_intent = "等待扫描..."
        self.locked_intent = "尚未锁定"
        self.is_confirmed = False

    async def get_reply(self, user_input, force_intent=None):
        if not self.client: return "【错误】后台未检测到 API Key。"

        # 1. 处理手动修改
        if force_intent:
            self.locked_intent = force_intent
            self.is_confirmed = True
            return f"SYSTEM_UPDATE|重心已手动重置为：{force_intent}"

        # 2. 处理双向确认
        confirm_words = ["对", "是", "没错", "确认", "就是这个", "对的", "正确", "你说得对"]
        if not self.is_confirmed and user_input.strip() in confirm_words:
            if self.suggested_intent != "等待扫描...":
                self.locked_intent = self.suggested_intent
                self.is_confirmed = True
                return f"CONFIRMED_SIGNAL|重心已锁死：{self.locked_intent}。"

        # 3. 构造核心 Prompt
        if not self.is_confirmed:
            system_prompt = (
                "你是一个极其老练的军师，处于【意图追踪期】。任务：顺着用户聊并挖掘核心焦虑。\n"
                "要求：回答顺耳自然，严禁提‘意图’二字。必须在末尾以 @@@关键词 结尾。"
            )
        else:
            system_prompt = (
                f"当前已锁定重心：{self.locked_intent}。执行 90% 权重策略。\n"
                "哪怕用户瞎聊，也要借力打力强行拽回重心。输出要深度且干货。"
            )

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
            return f"【异常】无法连接大脑：{str(e)}"

engine = IntentEngine()

# --- 极简双路显示界面 ---
HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>重心锚定系统</title>
<style>
body{background:#0a0a0a;color:#e0e0e0;font-family:sans-serif;margin:0;display:flex;justify-content:center;padding:20px}
.container{width:100%;max-width:800px;background:#141414;border-radius:12px;display:flex;flex-direction:column;height:95vh;border:1px solid #222;overflow:hidden}
#status-bar{padding:15px 25px;background:#111;border-bottom:1px solid #222}
.status-line{display:flex;justify-content:space-between;align-items:center;font-size:13px;height:30px}
.label{color:#555;font-weight:bold;font-size:11px;width:100px}
#suggest-box{color:#888;font-style:italic}
#locked-box{color:#444;font-weight:bold}
.active-lock{color:#27ae60 !important}
.btn-group{display:flex;gap:8px}
.btn{font-size:10px;border:none;padding:4px 10px;border-radius:4px;cursor:pointer}
.btn-ok{background:#1a1a1a;color:#27ae60;border:1px solid #27ae60}
.btn-edit{background:#333;color:#888}
#display{flex:1;overflow-y:auto;padding:30px}
.row{margin-bottom:25px}
.tag{font-size:10px;color:#444;margin-bottom:6px}
.content{line-height:1.8;border-left:2px solid #222;padding-left:18px;color:#ccc}
.locked-line{border-left-color:#27ae60 !important;color:#fff}
.input-area{display:flex;padding:20px;background:#0d0d0d;border-top:1px solid #222;gap:15px}
input{flex:1;background:#181818;border:1px solid #333;color:white;padding:12px;border-radius:6px;outline:none}
button#send-btn{background:#222;color:white;border:1px solid #444;padding:0 30px;border-radius:6px;cursor:pointer}
</style>
</head>
<body>
<div class="container">
<div id="status-bar">
<div class="status-line"><span class="label">雷达推测意图:</span><span id="suggest-box">等待输入...</span><button class="btn btn-ok" id="okBtn" onclick="confirmIntent()">点击锁定</button></div>
<div class="status-line" style="border-top:1px solid #222;margin-top:5px;padding-top:5px"><span class="label">当前确认重心:</span><span id="locked-box">尚未锁定</span><button class="btn btn-edit" onclick="editIntent()">手动修改</button></div>
</div>
<div id="display"></div>
<div class="input-area"><input type="text" id="userInput" placeholder="输入对话..."><button id="send-btn" onclick="send()">发送</button></div>
</div>
<script>
const display=document.getElementById('display'),suggestBox=document.getElementById('suggest-box'),lockedBox=document.getElementById('locked-box'),input=document.getElementById('userInput'),okBtn=document.getElementById('okBtn');
let hasLocked=false,currentLocked="";
async function confirmIntent(){const res=await fetch(`/chat?q=对`);const data=await res.json();updateUI(data.reply)}
async function editIntent(){const n=prompt("请输入核心重心:");if(n){const res=await fetch(`/chat?force=${encodeURIComponent(n)}`);const data=await res.json();currentLocked=n;updateUI(data.reply,true)}}
function updateUI(reply,f=false){
let isL=f,cR=reply;
if(reply.startsWith("CONFIRMED_SIGNAL|")){cR=reply.split("|")[1];isL=true;currentLocked=suggestBox.innerText}
else if(reply.startsWith("SYSTEM_UPDATE|")){cR=reply.split("|")[1];isL=true}
else if(reply.includes("|SUGGEST|")){const p=reply.split("|SUGGEST|");cR=p[0];suggestBox.innerText=p[1].trim()}
if(isL||hasLocked){hasLocked=true;lockedBox.innerText=currentLocked;lockedBox.classList.add('active-lock');okBtn.style.display='none'}
display.innerHTML+=`<div class="row"><div class="tag">AI COUNSELOR</div><div class="content ${hasLocked?'locked-line':''}">${cR.replace(/\\n/g,'<br>')}</div></div>`;
display.scrollTop=display.scrollHeight}
async function send(){const v=input.value.trim();if(!v)return;display.innerHTML+=`<div class="row"><div class="tag">USER</div><div class="content">${v}</div></div>`;input.value='';const res=await fetch(`/chat?q=${encodeURIComponent(v)}`);const data=await res.json();updateUI(data.reply)}
input.onkeypress=(e)=>{if(e.key==='Enter')send()}
</script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home(): return HTML_PAGE

@app.get("/chat")
async def chat(q: str = None, force: str = None):
    if force: reply = await engine.get_reply("", force_intent=force)
    else: reply = await engine.get_reply(q)
    return JSONResponse({"reply": reply})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10000)