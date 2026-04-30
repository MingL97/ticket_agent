# knowledge_base.py
from typing import List, Dict

class KnowledgeBase:
    """
    简单的知识库（FAQ + 解决方案）
    实际生产环境可替换为向量数据库
    """
    
    def __init__(self):
        self.entries = [
            {
                "id": 1,
                "keywords": ["无法登录", "登录不上", "密码错误"],
                "solution": "请尝试点击「忘记密码」重置，或检查网络连接后重新登录",
                "category": "技术故障"
            },
            {
                "id": 2,
                "keywords": ["退货", "退款", "不满意质量"],
                "solution": "请提供订单号和商品照片，客服将为您发起退货流程",
                "category": "退换货"
            },
            {
                "id": 3,
                "keywords": ["重复扣费", "多扣钱", "扣了两次"],
                "solution": "已记录您的反馈，将在 1 个工作日内核实并退还多扣金额",
                "category": "账单问题"
            },
            {
                "id": 4,
                "keywords": ["怎么用", "教程", "使用说明"],
                "solution": "请访问 help.example.com/guide 查看详细使用教程",
                "category": "咨询"
            }
        ]
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """基于关键词匹配的知识库检索"""
        query_lower = query.lower()
        results = []
        
        for entry in self.entries:
            score = 0
            for keyword in entry["keywords"]:
                if keyword in query_lower:
                    score += 1
            if score > 0:
                results.append({
                    **entry,
                    "match_score": score
                })
        
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results[:top_k]