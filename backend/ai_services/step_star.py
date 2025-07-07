# backend/ai_services/step_star.py

class StepChatAI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.stepfun.com/v1"

    def generate_response(self, prompt):
        # 移除 self.client 相关API调用，改为 raise NotImplementedError 或 pass
        raise NotImplementedError("StepStarAI 目前未实现 API 调用逻辑，请补充实现。")