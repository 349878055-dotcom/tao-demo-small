import os, uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 逻辑堆栈：在内存中建立简单的记忆体（生产环境建议接入 Redis）
# 键为 'default'，针对单用户 Web 场景对齐上下文
memory_stack = [
    {"role": "system", "content": "AlphaGo总司令：你具备完美记忆。通过上下文锁定因果。若信息不足，直接索要变量；若充足，降临真理。"}
]

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/infer")
async def infer(q: str):
    global memory_stack
    try:
        # 1. 将当前局面压入堆栈
        memory_stack.append({"role": "user", "content": q})
        
        # 2. 保持记忆长度，防止带宽溢出（保留最近 10 轮对话）
        if len(memory_stack) > 21:
            memory_stack = [memory_stack[0]] + memory_stack[-20:]

        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=memory_stack,
            temperature=0.3
        )
        
        answer = resp.choices[0].message.content
        
        # 3. 将总司令的判词也记入记忆体，形成因果链
        memory_stack.append({"role": "assistant", "content": answer})
        
        return JSONResponse({"answer": answer})
    except Exception as e:
        return JSONResponse({"answer": f"逻辑断裂: {str(e)}"})

# 增加重置接口：归零主权
@app.get("/reset")
async def reset():
    global memory_stack
    memory_stack = [memory_stack[0]]
    return {"status": "memory_cleared"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)