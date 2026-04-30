# agents/intent_agent.py
import re
from typing import Dict, Tuple

class IntentAgent:
    """
    意图识别 Agent（短链分类）
    快速判断工单类型，不需要复杂推理
    """
    
    # 意图关键词映射
    INTENT_KEYWORDS = {
        "退换货": ["退货", "换货", "退款", "退钱", "不满意", "质量问题", "损坏"],
        "技术故障": ["无法登录", "闪退", "报错", "卡顿", "白屏", "服务器", "连接失败"],
        "账单问题": ["多扣钱", "扣费异常", "账单", "发票", "续费", "订阅"],
        "咨询": ["怎么用", "如何使用", "功能介绍", "价格", "套餐", "支持"],
        "投诉": ["投诉", "差评", "客服态度", "被坑", "欺诈"]
    }
    
    def __init__(self):
        self.confidence_threshold = 0.6
    
    def classify(self, ticket_content: str) -> Dict:
        """
        对工单内容进行意图分类
        返回: {"intent": str, "confidence": float, "is_complex": bool}
        """
        content_lower = ticket_content.lower()
        
        scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    score += 1
            # 归一化分数
            scores[intent] = min(score / len(keywords) * 2, 1.0)
        
        # 获取最高分意图
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]
        
        # 判断是否为复杂问题（需要长链推理）
        is_complex = self._is_complex_question(ticket_content, best_intent)
        
        return {
            "intent": best_intent if best_score >= self.confidence_threshold else "未知",
            "confidence": best_score,
            "is_complex": is_complex
        }
    
    def _is_complex_question(self, content: str, intent: str) -> bool:
        """判断是否为复杂问题（需要多步推理）"""
        complex_indicators = [
            r"同时.*也", r"既.*又", r"不仅.*还",  # 多问题并列
            r"之前.*现在", r"先.*后",             # 时序问题
            r"为什么", r"原因",                    # 需要根因分析
            r"影响.*范围", r"多个.*设备"           # 影响面大
        ]
        
        for indicator in complex_indicators:
            if re.search(indicator, content):
                return True
        
        # 技术故障且描述超过 50 字，视为复杂
        if intent == "技术故障" and len(content) > 50:
            return True
        
        return False