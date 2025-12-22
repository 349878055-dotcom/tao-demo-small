import os
import uvicorn
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

app = FastAPI()

class StrategicConsultant:
    def __init__(self):
        # 建议在 Render 的 Environment Variables 中设置 OPENAI_API_KEY
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    async def get_inference(self, user_input):
        """第一步：多语言探测 - 无论什么语言，都要穿透意图"""
        if not self.client: return {"main": "", "hidden": "", "chat_reply": "Key未配置"}
        
        # 全语种核心指令：剥离语言外壳，直达利益本质
        system_logic = """
        You are a Top-tier Strategic Consultant skilled in Game Theory and Intelligence Analysis.
        
        [Core Task]
        Regardless of the input language (Chinese, Indonesian, English, etc.):
        1. Peel off emotional rhetoric and cultural politeness (especially in Asian/Southeast Asian contexts).
        2. Extract core interests: Assets, Power, Money, or Risks.
        3. Identify the 'Main Conflict' and 'Hidden Intent'.
        
        [Output Language]
        - Keep 'chat_reply' in the SAME language as the user's input to maintain rapport.
        - Output 'main' and 'hidden' in Chinese (or the user's preferred professional language) for maximum strategic clarity.
        
        Must output in STRICT JSON format.
        """

        messages = [
            {"role": "system", "content": system_logic},
            {"role": "user", "content": f"Input Material: {user_input}\nPlease provide JSON: {{'chat_reply': '...', 'main': '...', 'hidden': '...'}}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={ "type": "json_object" },
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"main": "Analysis Error", "hidden": "Analysis Error", "chat_reply": f"Error: {str(e)}"}

    async def get_deep_analysis(self, target):
        """第二步：深度下钻 - 跨语言逻辑推演"""
        
        structured_prompt = f"""
        【Strategic Target】: {target}
        
        Perform a deep logical deduction. Even if the input was in another language, your analysis must be sharp and professional.
        
        Structure:
        1. [Underlying Logic]: Power structure and original drivers.
        2. [Core Conflict]: The irreconcilable clash beneath the surface.
        3. [Path Deduction]: Two possible outcomes of this game.
        4. [Strategic Questions]: 3 high-quality questions to expose the truth.

        Language: Provide the analysis in Chinese (Academic Stanford Style) unless otherwise specified.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a cold, rational strategic expert. You expose conflicts that others try to hide."},
                    {"role": "user", "content": structured_prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Analysis failed: {str(e)}"

consultant = StrategicConsultant()

@app.get("/", response_class=HTMLResponse)
async def home():
    # 确保你的 index.html 放在同级目录下
    try:
        with open("index.html", "r", encoding="utf-8") as f: 
            return f.read()
    except:
        return "Index.html not found. Please check your file structure."

@app.get("/infer")
async def infer(q: str):
    data = await consultant.get_inference(q)
    return JSONResponse(data)

@app.get("/analyze")
async def analyze(target: str):
    return await consultant.get_deep_analysis(target)

if __name__ == "__main__":
    # host='0.0.0.0' 是 Render 等云平台部署的必须设置
    uvicorn.run(app, host="0.0.0.0", port=8000)