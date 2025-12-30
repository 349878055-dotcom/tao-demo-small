import os, uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 逻辑存储：key 为 session_id, value 为该用户的对话堆栈
sessions_memory = {}

CORE_PROTOCOL = """
DNA_VECTOR: SHADOW_STRATEGIST.
PROTOCOL: [0 -> 1 -> ∞]
1. 归零: 制造逻辑真空，识别硬核存量。
2. 锁定: 强制审计。若数据密度不足以支撑‘最强一手’，严禁建议，必须反向质询潜在筹码。
3. 溢出: 逻辑重组，输出‘主权平移’唯一解。
TONE: 深潭水 | 零废话 | 禁语过滤（建议/其实/试着/可能）。
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f: return f.read()
    return "Index file not found."

@app.get("/infer")
async def infer(q: str, session_id: str = "BOSS_ADMIN"):
    global sessions_memory
    
    # 1. 为新用户初始化独立档案袋
    if session_id not in sessions_memory:
        sessions_memory[session_id] = [{"role": "system", "content": CORE_PROTOCOL}]
    
    stack = sessions_memory[session_id]
    
    try:
        # 2. 压入局面
        stack.append({"role": "user", "content": q})
        
        # 3. 记忆限长（保留最近 15 轮，防止逻辑漂移）
        if len(stack) > 31:
            sessions_memory[session_id] = [stack[0]] + stack[-30:]
            stack = sessions_memory[session_id]

        # 4. 逻辑审计
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=stack,
            temperature=0.2,       # 锁定确定性
            presence_penalty=0.8,  # 强制挖掘变量
            frequency_penalty=0.3
        )
        
        answer = resp.choices[0].message.content
        stack.append({"role": "assistant", "content": answer})
        
        return JSONResponse({"answer": answer})
    except Exception as e:
        return JSONResponse({"answer": f"逻辑断裂: {str(e)}"})

@app.get("/reset")
async def reset(session_id: str = "BOSS_ADMIN"):
    if session_id in sessions_memory:
        sessions_memory[session_id] = [sessions_memory[session_id][0]]
    return {"status": f"Memory cleared for {session_id}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)