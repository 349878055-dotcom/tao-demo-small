import os
import uvicorn
import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from openai import OpenAI

app = FastAPI()

class StrategicConsultant:
    def __init__(self):
        # API Key 从环境变量读取
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    async def get_inference(self, user_input):
        """第一步：全语种识别 + 利益探测 + 四维人格量化扫描"""
        if not self.client: 
            return {"main": "Key未配置", "hidden": "Key未配置", "chat_reply": "请先配置 API Key"}
        
        system_logic = """
        You are a Top-tier Strategic Consultant. 
        Analyze the input (Indonesian, English, Chinese, etc.) and extract core game elements.
        
        [Four-Dimensional Personality Model] - Quantify from 0-100:
        - will: Will to Power (Dominance/Ambition)
        - moral: Moral Cost (Ethics/Restraint)
        - cognitive: Cognitive Horizon (Vision/Strategic depth)
        - base: Emotional Base (Stability/Security)

        [Output Guidelines]
        - 'chat_reply': Respond in the SAME language as user input.
        - 'main': Precise conflict in Chinese (Max 15 words).
        - 'hidden': Real intent in Chinese (Max 15 words).
        
        [Output JSON ONLY]
        {
          "chat_reply": "...",
          "main": "...",
          "hidden": "...",
          "persona_tags": ["标签1", "标签2"],
          "persona_brief": "对该人格的底层总结(中文, 20字内)",
          "weights": {"will": 0, "moral": 0, "cognitive": 0, "base": 0}
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
            return {"main": "探测失败", "hidden": str(e), "chat_reply": "System Error"}

    async def get_deep_analysis(self, target, raw_input, persona_brief, weights):
        """第二步：全维度记忆联动。带入原始素材、人格画像和权重进行分析。"""
        # 将上一轮的人格权重和素材注入上下文
        context_box = f"【博弈历史记忆】：{raw_input}\n【对手人格定性】：{persona_brief}\n【实时权重数据】：{weights}"
        
        structured_prompt = f"""
        {context_box}
        【当前研判重心】：{target}
        
        作为顶级战略幕僚，请结合上述【人格权重】执行深度博弈分析。
        1. 必须根据权力意志、道德成本等数值进行战术推演。
        2. 严禁哲学废话，每个结论必须有素材细节支撑。
        
        ### 01 【博弈人格与行为逻辑印证】
        ### 02 【核心冲突的逻辑再解构】
        ### 03 【针对性压制策略】
        ### 04 【致命级战略追问】
        
        语言：中文。风格：学术、冷峻、刀刀见血。
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你拥有完美记忆，擅长利用人格缺陷进行博弈建模。回复必须详尽。"},
                    {"role": "user", "content": structured_prompt}
                ],
                temperature=0.5
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"深度研判生成失败: {str(e)}"

consultant = StrategicConsultant()

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f: return f.read()
    except: return "Critical Error: index.html not found."

@app.get("/infer")
async def infer(q: str):
    return JSONResponse(await consultant.get_inference(q))

@app.get("/analyze")
async def analyze(target: str, raw: str, persona: str, weights: str):
    # 此处接收前端回传的所有记忆碎片
    return await consultant.get_deep_analysis(target, raw, persona, weights)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)