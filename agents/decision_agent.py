# agents/decision_agent.py
from typing import Dict, List
from datetime import datetime

class DecisionAgent:
    """
    决策 Agent
    根据意图识别和长链推理结果，决定：
    - 自动答复
    - 升级人工
    - 转派特定部门
    """
    
    # 部门路由映射
    ROUTING_RULES = {
        "退换货": "售后部门",
        "技术故障": "技术支撑部门",
        "账单问题": "财务部门",
        "投诉": "客诉部门",
        "咨询": "在线客服"
    }
    
    # 自动答复模板
    AUTO_REPLY_TEMPLATES = {
        "退换货": "您好，关于退换货问题，请提供订单号，我们将在 2 小时内为您处理。",
        "咨询": "感谢您的咨询。请问您需要了解哪个方面的详细信息？",
        "账单问题_low": "您好，已为您查询账单详情，请查收附件。如有疑问可继续咨询。"
    }
    
    def decide(self, intent_result: Dict, reasoning_result: Dict, ticket: Dict) -> Dict:
        """
        决策主逻辑
        """
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        is_complex = intent_result["is_complex"]
        need_human = reasoning_result.get("need_human_escalation", False)
        
        # 决策树
        decision = {
            "ticket_id": ticket.get("id"),
            "timestamp": datetime.now().isoformat(),
            "action": None,
            "target": None,
            "auto_reply": None,
            "reasoning": []
        }
        
        # 规则 1: 低置信度 -> 转人工
        if confidence < 0.5:
            decision["action"] = "escalate_to_human"
            decision["target"] = "人工客服"
            decision["reasoning"].append(f"意图识别置信度低 ({confidence:.2f})，需人工介入")
        
        # 规则 2: 复杂问题 + 需要升级 -> 转人工
        elif is_complex and need_human:
            decision["action"] = "escalate_to_human"
            decision["target"] = "人工客服"
            decision["reasoning"].append("问题复杂程度超出自动处理范围")
        
        # 规则 3: 技术故障且有历史模式 -> 转技术部门
        elif intent == "技术故障" and reasoning_result.get("historical_pattern"):
            decision["action"] = "route_to_department"
            decision["target"] = self.ROUTING_RULES.get(intent, "技术支撑部门")
            decision["reasoning"].append("历史复现问题，需要技术深度排查")
        
        # 规则 4: 高严重性 -> 优先处理 + 转部门
        elif reasoning_result.get("root_cause", {}).get("severity") == "high":
            decision["action"] = "route_to_department"
            decision["target"] = self.ROUTING_RULES.get(intent, "客诉部门")
            decision["priority"] = "high"
            decision["reasoning"].append(f"严重性高，需 {decision['target']} 优先处理")
        
        # 规则 5: 可自动答复
        else:
            decision["action"] = "auto_reply"
            decision["target"] = "用户"
            decision["auto_reply"] = self._generate_auto_reply(intent, reasoning_result, ticket)
            decision["reasoning"].append("符合自动答复条件")
        
        return decision
    
    def _generate_auto_reply(self, intent: str, reasoning_result: Dict, ticket: Dict) -> str:
        """生成自动答复内容"""
        # 优先使用推理出的解决方案路径
        if reasoning_result.get("solution_path"):
            steps = reasoning_result["solution_path"]
            reply = "您好，根据系统分析，建议您按以下步骤操作：\n"
            for step in steps:
                reply += f"- {step}\n"
            reply += "\n如问题仍未解决，请回复此消息，我们将安排人工客服跟进。"
            return reply
        
        # 使用模板
        if intent in self.AUTO_REPLY_TEMPLATES:
            return self.AUTO_REPLY_TEMPLATES[intent]
        
        # 默认答复
        return "您好，您的工单已收到。我们正在处理中，将在 24 小时内回复您。"