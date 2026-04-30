# agents/reasoning_agent.py
from typing import Dict, List, Optional
import json

class ReasoningAgent:
    """
    长链推理 Agent
    处理复杂问题，进行多步推理：
    1. 拆解问题
    2. 检索历史记录
    3. 查找知识库
    4. 推理根本原因
    5. 生成解决方案路径
    """
    
    def __init__(self, knowledge_base):
        self.kb = knowledge_base
        self.reasoning_steps = []
    
    def analyze(self, ticket: Dict, user_history: List[Dict]) -> Dict:
        """
        长链推理主入口
        """
        content = ticket["content"]
        
        self.reasoning_steps = []
        
        # Step 1: 问题拆解
        sub_issues = self._decompose_issue(content)
        self.reasoning_steps.append(f"问题拆解为 {len(sub_issues)} 个子问题: {sub_issues}")
        
        # Step 2: 历史记录分析
        historical_pattern = self._analyze_history(user_history)
        if historical_pattern:
            self.reasoning_steps.append(f"历史分析: {historical_pattern}")
        
        # Step 3: 知识库匹配
        kb_results = self._search_knowledge_base(content)
        self.reasoning_steps.append(f"知识库匹配到 {len(kb_results)} 条相关条目")
        
        # Step 4: 根因推理（链式推理）
        root_cause = self._infer_root_cause(content, historical_pattern, kb_results)
        self.reasoning_steps.append(f"根因推理结果: {root_cause}")
        
        # Step 5: 生成解决方案路径
        solution_path = self._generate_solution_path(root_cause, kb_results)
        
        return {
            "sub_issues": sub_issues,
            "historical_pattern": historical_pattern,
            "root_cause": root_cause,
            "solution_path": solution_path,
            "reasoning_trace": self.reasoning_steps,
            "need_human_escalation": len(sub_issues) > 3 or root_cause.get("severity") == "high"
        }
    
    def _decompose_issue(self, content: str) -> List[str]:
        """将复杂问题拆解为多个子问题"""
        sub_issues = []
        
        # 按标点符号拆分
        sentences = content.replace("？", "。").replace("；", "。").split("。")
        
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 5 and ("?" in sent or "？" in sent or "如何" in sent or "怎么" in sent):
                sub_issues.append(sent)
        
        if not sub_issues:
            sub_issues = [content[:50] + "..."]
        
        return sub_issues
    
    def _analyze_history(self, history: List[Dict]) -> Optional[str]:
        """分析用户历史工单，发现模式"""
        if len(history) < 2:
            return None
        
        # 统计历史意图分布
        intent_count = {}
        for ticket in history:
            intent = ticket.get("intent", "未知")
            intent_count[intent] = intent_count.get(intent, 0) + 1
        
        most_common = max(intent_count, key=intent_count.get)
        
        if intent_count.get(most_common, 0) >= 3:
            return f"用户频繁提交 {most_common} 类问题，可能存在系统性问题或用户操作误区"
        
        return None
    
    def _search_knowledge_base(self, content: str) -> List[Dict]:
        """搜索知识库（简化版）"""
        return self.kb.search(content, top_k=3)
    
    def _infer_root_cause(self, content: str, history_pattern: Optional[str], kb_results: List[Dict]) -> Dict:
        """
        链式推理根本原因
        使用 if-else 推理链模拟
        """
        content_lower = content.lower()
        
        # 推理链 1: 登录/账户问题
        if "登录" in content_lower or "无法登录" in content_lower:
            if "忘记密码" in content_lower:
                return {"cause": "用户忘记密码", "severity": "low", "action": "发送密码重置指引"}
            elif "账号被锁" in content_lower or "多次尝试" in content_lower:
                return {"cause": "账号因多次失败尝试被锁定", "severity": "medium", "action": "解锁账号并提醒用户"}
            else:
                return {"cause": "可能是会话过期或网络问题", "severity": "medium", "action": "引导用户清除缓存或检查网络"}
        
        # 推理链 2: 支付/账单问题
        if "扣费" in content_lower or "账单" in content_lower:
            if "重复" in content_lower or "两次" in content_lower:
                return {"cause": "重复扣费（可能是接口超时重试导致）", "severity": "high", "action": "发起退款流程并通知财务"}
            elif "没收到" in content_lower and "服务" in content_lower:
                return {"cause": "支付成功但服务未激活", "severity": "high", "action": "手动激活服务并补发通知"}
            else:
                return {"cause": "账单周期理解偏差或套餐变更导致", "severity": "low", "action": "发送账单明细解释"}
        
        # 推理链 3: 性能/故障问题
        if "卡" in content_lower or "慢" in content_lower or "闪退" in content_lower:
            if history_pattern and "技术故障" in history_pattern:
                return {"cause": "历史复发性问题，可能是设备兼容性或特定版本 Bug", "severity": "high", "action": "升级为技术工单，指派开发人员"}
            else:
                return {"cause": "可能是临时性性能波动", "severity": "low", "action": "建议用户稍后重试，同时监控服务状态"}
        
        # 默认
        return {"cause": "需人工进一步确认", "severity": "medium", "action": "转人工客服"}
    
    def _generate_solution_path(self, root_cause: Dict, kb_results: List[Dict]) -> List[str]:
        """生成解决方案路径"""
        steps = []
        
        # 根据根因生成步骤
        if root_cause.get("action"):
            steps.append(f"1. {root_cause['action']}")
        
        # 从知识库补充
        if kb_results:
            best_match = kb_results[0]
            if "solution" in best_match:
                steps.append(f"2. {best_match['solution']}")
        
        if not steps:
            steps.append("建议转人工客服处理")
        
        return steps