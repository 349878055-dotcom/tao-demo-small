import os
import uvicorn
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

app = FastAPI()

class StrategicConsultant:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.history = []

    async def get_inference(self, user_input):
        """第一步：获取普通回答并同步探测重心"""
        if not self.client: return {"main": "", "hidden": "", "chat_reply": "Key未配置"}
        
        # 强制要求JSON输出
        messages = [
            {"role": "system", "content": "你是一个战略决策助手。请先像ChatGPT一样提供普通回复，并提取核心意图。"},
            {"role": "user", "content": f"输入: {user_input}\n请回复一段200字内的分析，并附带JSON格式的'main'(主要矛盾)和'hidden'(潜在意图)。格式要求: {{'chat_reply': '...', 'main': '...', 'hidden': '...'}}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={ "type": "json_object" }, # 强制JSON格式输出
                temperature=0.7
            )
            data = json.loads(response.choices[0].message.content)
            self.history.append({"role": "user", "content": user_input})
            return data
        except Exception as e:
            return {"main": "解析异常", "hidden": "解析异常", "chat_reply": f"对话异常: {str(e)}"}

    async def get_deep_analysis(self, target):
        """第二步：下钻深度分析 - 已修改为结构化推导与高质量追问模式"""
        
        # 构建深度结构化指令
        structured_prompt = f"""
        【绝对重心锁定】：{target}
        
        作为顶级战略幕僚，请针对该重心进行深度逻辑推演，必须严格执行以下结构：

        1. 【底层逻辑拆解】：
           分析该事项在商业或博弈层面的原始驱动力与权力分配结构。
        
        2. 【主要矛盾暴露】：
           一针见血地指出潜伏在表象下的“不可调和冲突”（如：信任与制度的冲突、短期利益与长期资产安全的冲突等）。
        
        3. 【逻辑路径推演】：
           基于目前已知情况，推演出两种可能的博弈走向或操作路径。
        
        4. 【战略级深度追问】：
           由于目前信息不全，请基于逻辑漏洞提出 3 个最能触及核心利益、最能引导客户说出实情的高质量问题。

        要求：语感专业、冷静，不回避问题，下钻到位。
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是一个极度理性的战略专家，擅长暴露主要矛盾和逻辑推演。"},
                {"role": "user", "content": structured_prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

consultant = StrategicConsultant()

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/infer")
async def infer(q: str):
    data = await consultant.get_inference(q)
    return JSONResponse(data)

@app.get("/analyze")
async def analyze(target: str):
    return await consultant.get_deep_analysis(target)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)