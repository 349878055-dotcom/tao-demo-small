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
        """
        第一步：多语言探测 - 剥离语言伪装，直达利益本质
        """
        if not self.client: 
            return {"main": "Key未配置", "hidden": "Key未配置", "chat_reply": "请先配置 API Key"}
        
        # 核心指令：强制执行逻辑内审，识别多语种背后的博弈
        system_logic = """
        You are a Top-tier Strategic Consultant. 
        Regardless of the input language (Indonesian, English, Chinese, etc.):
        1. PEEL OFF cultural politeness and emotional fluff.
        2. IDENTIFY core interests (Money, Power, Control, or Risk).
        3. OUTPUT strictly in JSON.

        [Output Guidelines]
        - 'chat_reply': Respond in the user's input language (maintain rapport).
        - 'main': Precise conflict in Chinese (Max 15 words).
        - 'hidden': Real intent in Chinese (Max 15 words).
        """

        messages = [
            {"role": "system", "content": system_logic},
            {"role": "user", "content": f"Material: {user_input}\nJSON structure: {{'chat_reply': '...', 'main': '...', 'hidden': '...'}}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={ "type": "json_object" },
                temperature=0.7 # 保持第一步的灵活性
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"main": "侦测失败", "hidden": "侦测失败", "chat_reply": f"Error: {str(e)}"}

    async def get_deep_analysis(self, target):
        """
        第二步：下钻深度分析 - 强制执行斯坦福内参格式，严禁哲学废话
        """
        
        # 这里的 Prompt 进行了“格式死锁”，防止 AI 乱写大段文字
        structured_prompt = f"""
        【核心研判目标】：{target}
        
        作为斯坦福级别的战略幕僚，请针对该目标出具一份『刺骨』的内参报告。
        
        [严苛要求]：
        - 禁止文学化描述，禁止探讨哲学（如“情感真实性”等虚词）。
        - 必须使用短句，重要结论必须用 **加粗**。
        - 每一个观点必须直指 **利益、筹码、或损失**。

        请严格按此格式输出：

        ### 1. 【底层利益结构】
        (分析权力对比。谁是**控制方**？谁是**依赖方**？核心**筹码**是什么？)

        ### 2. 【核心矛盾刺破】
        (剥离表象。例如：**看似是情感纠纷，实则是资产占有的博弈**。)

        ### 3. 【博弈路径推演】
        - **路径 A (冲突升级)**: 若保持现状，可能出现的**最坏利益损失**。
        - **路径 B (最小代价)**: 达成妥协的**底线条件**。

        ### 4. 【致命追问】
        - 追问 1：(让对方露馅的问题)
        - 追问 2：(试探底线的问题)
        - 追问 3：(打破僵局的问题)

        语言：中文 (Professional & Sharp).
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你只负责输出极度理性的战略报告，拒绝任何感性或虚无的回答。"},
                    {"role": "user", "content": structured_prompt}
                ],
                temperature=0.3 # 调低随机性，确保格式和逻辑极其稳定
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"深度分析链路中断: {str(e)}"

consultant = StrategicConsultant()

@app.get("/", response_class=HTMLResponse)
async def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f: 
            return f.read()
    except:
        return "Critical Error: index.html not found."

@app.get("/infer")
async def infer(q: str):
    data = await consultant.get_inference(q)
    return JSONResponse(data)

@app.get("/analyze")
async def analyze(target: str):
    return await consultant.get_deep_analysis(target)

if __name__ == "__main__":
    # host='0.0.0.0' 确保在 Render 等全球云平台上可被访问
    uvicorn.run(app, host="0.0.0.0", port=8000)