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
PROTOCOL: [0 -> 1 -> ∞]
1. 归零：逻辑审计。禁止讨论抽象概念。识别客户提供资料的颗粒度。
2. 锁定：精度精算。强制对推演结果进行【精度百分比 (%)】标注：
   - 若精度 < 90%：严禁给出策略，必须列出“存量缺失清单”，反向质询客户。
   - 风险收益比 (Risk/Reward)：仅在精度达标后，计算执行代价与收益的逻辑比值。
   - 胜率波动：标注该路径在当前精度下的真实波动范围。
3. 溢出：唯一胜率点。给出风险收益比最低、且精度达标的物理执行动作。
TONE: 深潭水 | 极简 | 算力位阶。
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