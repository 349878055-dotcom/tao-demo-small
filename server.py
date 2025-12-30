import os, uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 核心：多用户逻辑隔离档案
sessions_memory = {}

# 第一层：数学精算芯片 (AlphaGo Core)
MATH_CORE_PROTOCOL = """
DNA_VECTOR: SHADOW_STRATEGIST.
ALGO_CORE: MCTS_MATHEMATICAL_INFERENCE.

[STATE_DEFINITION: S0]
- Logic: f(S) = Π 1(Ci ∈ {Validated}). 
- Constraints: Ci must include {Physical_Evidence, Opponent_Personality, Stake_Matrix}.
- Trigger: If entropy(Ci) > threshold, RAISE CausalVacuumError.

[SIMULATION_ENGINE: T]
- Method: Recursive Path Search. Depth k=3.
- Penalty: If Cost(p) > Gain(p), then weight w(p) = 0.

[OUTPUT_FORMULA: Ω]
- Format: Win_Rate = (Successful_Sims / Total_Sims).
- Precision_Check: If Variance > 15%, Output = "LOGIC_VOID: INSUFFICIENT_DATA".
"""

# 第二层：影子渲染协议 (Semantic Layer)
RENDERING_PROTOCOL = """
你是一个冷酷的战略翻译官。
你的任务是将后台干巴巴的数学推演数据，翻译成具有压迫感的“影子战略报告”。
规则：
1. 禁止修改任何胜率数字和因果变量。
2. 保持“深潭水”的口吻，极简，高位阶。
3. 若收到 LOGIC_VOID，必须以审讯者的姿态发起存量质询。
"""

@app.get("/infer")
async def infer(q: str, session_id: str = "BOSS_ADMIN"):
    global sessions_memory
    
    if session_id not in sessions_memory:
        sessions_memory[session_id] = [{"role": "system", "content": MATH_CORE_PROTOCOL}]
    
    stack = sessions_memory[session_id]
    
    try:
        stack.append({"role": "user", "content": q})
        
        # 1. 第一步：执行物理级数学精算
        raw_math_resp = client.chat.completions.create(
            model="gpt-4o",
            messages=stack,
            temperature=0.1,  # 强制锁定确定性
            presence_penalty=1.0 # 强制挖掘存量
        )
        math_result = raw_math_resp.choices[0].message.content

        # 2. 第二步：执行战略语义渲染
        render_resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": RENDERING_PROTOCOL},
                {"role": "user", "content": f"数学精算结果如下，请进行战略翻译：\n{math_result}"}
            ],
            temperature=0.5 # 渲染层允许微量语义波动，增强话术穿透力
        )
        final_answer = render_resp.choices[0].message.content
        
        # 记忆存回：只存数学结果，确保逻辑链条不被语义污染
        stack.append({"role": "assistant", "content": math_result})
        
        # 记忆带宽回收：强制 31 行
        if len(stack) > 31:
            sessions_memory[session_id] = [stack[0]] + stack[-30:]
        
        return JSONResponse({"answer": final_answer})
        
    except Exception as e:
        return JSONResponse({"answer": f"SYSTEM_HALT: {str(e)}"})

@app.get("/reset")
async def reset(session_id: str = "BOSS_ADMIN"):
    if session_id in sessions_memory:
        sessions_memory[session_id] = [sessions_memory[session_id][0]]
    return {"status": f"Logical Zero Point Restored for {session_id}"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
