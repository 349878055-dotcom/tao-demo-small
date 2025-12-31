import os, uvicorn, traceback
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI

class ArcheologyRequest(BaseModel):
    input: str

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- [∞: 主权接管/因果率] 唯一算子 ---
CORE_LOGIC = """[∞: 主权接管/因果率]
1. 归零 (Pressure Gap): 撤销一切局部支撑，制造逻辑绝对真空。屏蔽感性噪音。
2. 锁定 (Rigid Coupling): 建立 A 与 B 的 1.0 关联，排除所有随机变量（感情、信任、沟通）。
3. 溢出 (Structural Re-coding): 顺势重塑因果定义，实现系统级主权接管。
任务：直接交付绝对行动指令。禁语：建议、可能、其实、希望、协商。"""

@app.post("/archeology")
async def execute_archeology(req: ArcheologyRequest):
    try:
        # 单步逻辑对撞：锁定 Temperature=0 确保因果率刚性
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": CORE_LOGIC}, 
                      {"role": "user", "content": req.input}],
            temperature=0
        )
        return {
            "mode": "SOVEREIGNTY_TAKEOVER", 
            "result": response.choices[0].message.content 
        }

    except Exception:
        return {"error": "LOGIC_COLLAPSE"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
