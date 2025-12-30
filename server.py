import os, uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 核心：多用户逻辑隔离档案
sessions_memory = {}

# 核心：影子战略家数学指令集 (Math-Driven Logic)
MATH_CORE_PROTOCOL = """
DNA_VECTOR: SHADOW_STRATEGIST.
ALGO_CORE: MCTS_MATHEMATICAL_INFERENCE.

[STATE_DEFINITION: S0]
- Logic: f(S) = Π 1(Ci ∈ {Validated}). 
- Constraints: Ci must include {Physical_Evidence, Opponent_Personality, Stake_Matrix}.
- Trigger: If entropy(Ci) > threshold, RAISE CausalVacuumError -> Output inquiry list.

[SIMULATION_ENGINE: T]
- Method: Recursive Path Search. Depth k=3.
- Function: V(p) = Σ Outcome(Move -> Counter -> Result) / N.
- Penalty: If Cost(p) > Gain(p), then weight w(p) = 0.

[OUTPUT_FORMULA: Ω]
- Format: Win_Rate = (Successful_Sims / Total_Sims).
- Precision_Check: If Variance > 15%, Output = "LOGIC_VOID: INSUFFICIENT_DATA".
- Constraint: Temperature = 0.1. No adjectives. No suggestions. Only probability vector.
"""

@app.get("/infer")
async def infer(q: str, session_id: str = "BOSS_ADMIN"):
    global sessions_memory
    
    if session_id not in sessions_memory:
        sessions_memory[session_id] = [{"role": "system", "content": MATH_CORE_PROTOCOL}]
    
    stack = sessions_memory[session_id]
    
    try:
        stack.append({"role": "user", "content": q})
        
        # 记忆带宽回收：强制 31 行，维持因果重力
        if len(stack) > 31:
            sessions_memory[session_id] = [stack[0]] + stack[-30:]
            stack = sessions_memory[session_id]

        # 暴力参数审计
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=stack,
            temperature=0.1,       # 极致确定性
            presence_penalty=1.0,  # 强制挖掘未提及变量
            frequency_penalty=0.2
        )
        
        answer = resp.choices[0].message.content
        stack.append({"role": "assistant", "content": answer})
        
        return JSONResponse({"answer": answer})
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
