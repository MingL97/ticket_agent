# utils.py
import json
from typing import List, Dict
from datetime import datetime

def load_tickets(filepath: str) -> List[Dict]:
    """加载工单数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_decision(decision: Dict, output_path: str):
    """保存决策结果"""
    with open(output_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(decision, ensure_ascii=False) + '\n')

def get_user_history(tickets: List[Dict], user_id: str, max_count: int = 5) -> List[Dict]:
    """获取用户历史工单"""
    history = [t for t in tickets if t.get("user_id") == user_id]
    return history[-max_count:]  # 最近 N 条

def format_output(decision: Dict) -> str:
    """格式化输出决策结果"""
    output = f"""
========== 工单 #{decision.get('ticket_id')} ==========
决策时间: {decision.get('timestamp')}
执行动作: {decision.get('action')}
目标对象: {decision.get('target')}
决策依据: {', '.join(decision.get('reasoning', []))}
"""
    if decision.get('auto_reply'):
        output += f"\n自动答复内容:\n{decision.get('auto_reply')}\n"
    if decision.get('priority'):
        output += f"优先级: {decision.get('priority')}\n"
    
    output += "=" * 40
    return output