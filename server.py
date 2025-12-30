import os, uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse  # 移除 HTMLResponse，因为不再渲染网页
from openai import OpenAI

app = FastAPI()
# 自动读取 Render 后台配置的环境变量，严禁手动填写 Key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 核心：多用户逻辑档案库
sessions_memory = {}

# 核心：影子战略家最高指令集（暴力加压版，杜绝废话）
CORE_PROTOCOL = """
DNA_VECTOR: SHADOW_STRATEGIST.
PROTOCOL: [0 -> 1 -> ∞]
1. 归零: 制造逻辑真空，识别硬核存量。严禁使用“建议/其实/保持冷静”等弱势词汇。
2. 锁定: 强制审计。若数据密度不足以支撑‘最强一手’，必须反向质询潜在筹码。
3. 溢出: 逻辑重组，输出具有“物理破坏性”的博弈策略。
TONE: 深潭水 | 极简 | 判官位阶。
"""

# --- 原 home 网页入口已物理移除，彻底实现主权回收 ---

# 核心推演接口：支持多用户隔离
@app.get("/infer")
async def infer(q: str, session_id: str = "BOSS_ADMIN"):
    global sessions_memory
    
    # 1. 自动识别 session_id，实现物理隔离
    if session_id not in sessions_memory:
        sessions_memory[session_id] = [{"role": "system", "content": CORE_PROTOCOL}]
    
    stack = sessions_memory[session_id]
    
    try:
        # 2. 压入新局面
        stack.append({"role": "user", "content": q})
        
        # 3. 记忆带宽回收：保持 31 行（约 15 轮对话），防止逻辑熵增
        if len(stack) > 31:
            sessions_memory[session_id] = [stack[0]] + stack[-30:]
            stack = sessions_memory[session_id]

        # 4. 高压审计：锁定低温度（确定性）与高惩罚（挖掘新变量）
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=stack,
            temperature=0.2,       # 杜绝废话，锁定唯一解
            presence_penalty=0.8,  # 强制 AI 挖掘客户未说出的筹码
            frequency_penalty=0.3
        )
        
        answer = resp.choices[0].message.content
        # 将回答存入对应用户的档案袋，维持连续记忆
        stack.append({"role": "assistant", "content": answer})
        
        return JSONResponse({"answer": answer})
    except Exception as e:
        return JSONResponse({"answer": f"逻辑断裂: {str(e)}"})

# 核心：主权归零接口（小程序新局按钮调用）
@app.get("/reset")
async def reset(session_id: str = "BOSS_ADMIN"):
    if session_id in sessions_memory:
        # 清空对应 ID 的记忆，只保留最底层的核心协议
        sessions_memory[session_id] = [sessions_memory[session_id][0]]
    return {"status": f"Memory cleared for {session_id}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)