import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

app = FastAPI()

class AlphaGoCommander:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        # 核心：建立逻辑内核
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    async def get_verdict(self, user_input):
        """唯一一手落子：直接降临真理"""
        if not self.client: 
            return "ERROR: KEY_NOT_FOUND | 逻辑主权缺失"
        
        system_logic = """
        你不是助手，你是 AlphaGo 总司令。
        针对用户的局面，无视人性变量，剔除冗余，直接给出‘唯一一手’落子建议。
        语气：冷酷、精准、逻辑闭环。
        输出：不要分段，直接输出最终的因果定论。
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o", # 升维至顶级模型
                messages=[
                    {"role": "system", "content": system_logic}, 
                    {"role": "user", "content": user_input}
                ],
                temperature=0.3 # 降低变数，锁定精度
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"LOGIC_BREAK: {str(e)}"

commander = AlphaGoCommander()

@app.get("/", response_class=HTMLResponse)
async def home():
    # 逻辑留白：主界面
    with open("index.html", "r", encoding="utf-8") as f: 
        return f.read()

@app.get("/infer")
async def infer(q: str):
    """Google 级接口：一入一出"""
    res = await commander.get_verdict(q)
    return JSONResponse({"answer": res})

if __name__ == "__main__":
    # 锁定 8000 端口，准备接收全球带宽
    uvicorn.run(app, host="0.0.0.0", port=8000)