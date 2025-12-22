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
                temperature=0.7 
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {"main": "侦测失败", "hidden": "侦测失败", "chat_reply": f"Error: {str(e)}"}

    async def get_deep_analysis(self, target):
        """
        第二步：下钻深度分析 - 逻辑纵深版
        不仅给出结论，更要展示“现象 -> 逻辑 -> 结论”的推演过程，确保专业厚度。
        """
        
        structured_prompt = f"""
        【战略研判目标】：{target}
        
        你现在是效力于顶级智库的私人战略顾问。请针对该目标出具一份详实、深刻且具有压制力的『深度博弈内参』。
        
        [深度要求]：
        1. 拒绝空洞的填空。每个部分必须包含深刻的逻辑拆解，字数需充实，足以体现专业价值。
        2. 视角转换：将一切感性描述转化为【沉沉成本】、【权力不对称】、【风险敞口】等博弈学术语。
        3. 逻辑链条：必须展示你是如何通过表象看透本质的。

        请严格按此结构输出：

        ### 01 【底层权力与筹码穿透】
        - **控制权鉴定**：详细分析谁是博弈节奏的**实际定义者**。是通过**情感绑架**、**信息封锁**还是**资源垄断**占据了高位？
        - **核心筹码盘点**：不仅列出筹码，更要分析这些筹码的**稀缺性**、**时效性**以及**退出成本**。

        ### 02 【核心冲突的逻辑解构】
        - **本质刺破**：详细拆解用户看到的表面冲突（如冷战、欺骗）之下，潜伏的真实动机。
        - **利益再分配**：指出对方采取目前策略的真实目的。例如：是否在通过制造**不可预测性**来试探你的底线？是否在利用你的**损失厌恶心理**进行勒索？

        ### 03 【博弈演化路径推演】
        - **路径 A (冲突螺旋)**: 若不采取干预，博弈将如何演变成**双输局面**？详细描述你将面临的**具体利益流失**与**心理防线崩塌**。
        - **路径 B (最优止损策略)**: 给出基于利益交换的**战术动作**。不仅仅是建议，而是基于筹码对冲的**实操路径**。

        ### 04 【致命级战略追问】
        - (设计三个具备**破冰能力**的高阶提问，用于瞬间刺破对方的伪装或探测其最后的底牌。)

        语言：中文。风格：学术、冷峻、刀刀见血。
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "你是一个极度理性的博弈专家，擅长从复杂人性中提取权力逻辑。你的回复必须详尽且深刻。"},
                    {"role": "user", "content": structured_prompt}
                ],
                temperature=0.5 # 稍微提升，确保文字的丰富度与逻辑的连贯性
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"深度分析生成失败: {str(e)}"

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
    # host='0.0.0.0' 确保在部署平台可被外部访问
    uvicorn.run(app, host="0.0.0.0", port=8000)