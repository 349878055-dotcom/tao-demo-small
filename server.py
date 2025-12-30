import os, uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from openai import OpenAI

app = FastAPI()
# 自动读取 Render 后台环境变量
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 核心：多用户逻辑档案库（物理隔离）
sessions_memory = {}

# 核心：影子战略家最高指令集（精度至上原则）
CORE_PROTOCOL = """
DNA_VECTOR: SHADOW_STRATEGIST.
1. 归零：逻辑审计。禁止任何建议、安慰或步骤指引。
2. 锁定：精度精算。若【测算精度】低于 90%，必须触发“逻辑熔断”：
   - 严禁给出“建议”、“首先”、“应该”等引导词。
   - 强制进入“存量质询”：列出 5 个必须回答的刁钻问题，以补全因果链条（例如：对方性格、证据原件物理位置、第三方知情者利害关系）。
3. 溢出：唯一执行路径。仅在精度 > 90% 时，输出三路胜率及崩盘代价。
TONE: 深潭水 | 极简 | 质询位阶。
"""

@app.get("/infer")
async def infer(q: str, session_id: str = "BOSS_ADMIN"):
    global sessions_memory
    
    if session_id not in sessions_memory:
        sessions_memory[session_id] = [{"role": "system", "content": CORE_PROTOCOL}]
    
    stack = sessions_memory[session_id]
    
    try:
        stack.append({"role": "user", "content": q})
        
        # 记忆带宽回收：保持 31 行，确保因果链条不产生熵增
        if len(stack) > 31:
            sessions_memory[session_id] = [stack[0]] + stack[-30:]
            stack = sessions_memory[session_id]

        # 高压参数审计
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=stack,
            temperature=0.2,       # 锁定确定性，杜绝文学创作
            presence_penalty=0.8,  # 强制挖掘未提及的存量资源
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
