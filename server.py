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

    async def get_inference(self, user_input):
        """兼容性扫描：识别 1-2 个角色，提取事实清单"""
        if not self.client: 
            return {"main": "Key未配置", "chat_reply": "请配置 API Key"}
        
        system_logic = """
        You are a Top-tier Strategic Consultant.
        [Task] Analyze the material. Identify up to TWO main game characters.
        [Weights] Quantify 0-100: will (dominance), moral (restraint), cognitive (vision), base (stability).
        
        [Output JSON ONLY]
        {
          "chat_reply": "与用户输入语言保持一致。",
          "main": "主要矛盾(中文, 15字内)",
          "hidden": "真实意图(中文, 15字内)",
          "facts": ["事实1", "事实2"],
          "persona_brief": "对局势中人物关系的定性",
          "characters": [
            { "name": "角色名称", "brief": "底色定性", "weights": {"will":0, "moral":0, "cognitive":0, "base":0} }
          ]
        }
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system_logic}, {"role": "user", "content": user_input}],
                response_format={ "type": "json_object" },
                temperature=0.7 
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"main": "扫描中断", "hidden": "通信异常", "characters": [], "chat_reply": "系统响应超时，请重试。"}

    async def get_deep_analysis(self, target, raw_input, char_data, facts, persona):
        """下钻分析：带入所有锁定记忆"""
        context = f"素材：{raw_input}\n事实：{facts}\n角色：{char_data}\n画像：{persona}"
        prompt = f"基于记忆库：\n{context}\n针对重心【{target}】进行穿透式博弈研判。"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "你拥有完美记忆，擅长利用人格漏洞反制对方。"}, {"role": "user", "content": prompt}],
                temperature=0.4
            )
            return response.choices[0].message.content
        except: return "深度研判暂时无法生成。"

consultant = StrategicConsultant()

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("index.html", "r", encoding="utf-8") as f: return f.read()

@app.get("/infer")
async def infer(q: str):
    return JSONResponse(await consultant.get_inference(q))

@app.get("/analyze")
async def analyze(target: str, raw: str, chars: str, facts: str, persona: str):
    return await consultant.get_deep_analysis(target, raw, chars, facts, persona)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)