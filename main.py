# main.py
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.intent_agent import IntentAgent
from agents.reasoning_agent import ReasoningAgent
from agents.decision_agent import DecisionAgent
from knowledge_base import KnowledgeBase
from utils import load_tickets, get_user_history, format_output


def main():
    print("=" * 60)
    print("智能工单分级与自动答复 Agent 系统")
    print("=" * 60)
    
    # 初始化组件
    intent_agent = IntentAgent()
    kb = KnowledgeBase()
    reasoning_agent = ReasoningAgent(kb)
    decision_agent = DecisionAgent()
    
    # 加载工单
    tickets = load_tickets("data/sample_tickets.json")
    
    # 处理每个工单
    for ticket in tickets:
        print(f"\n📨 处理工单 #{ticket['id']}: {ticket['content'][:50]}...")
        
        # Step 1: 意图识别（短链）
        intent_result = intent_agent.classify(ticket["content"])
        print(f"   🧠 意图识别: {intent_result['intent']} (置信度: {intent_result['confidence']:.2f})")
        
        # Step 2: 获取用户历史
        history = get_user_history(tickets, ticket["user_id"])
        
        # Step 3: 如果是复杂问题，进行长链推理
        if intent_result["is_complex"]:
            print(f"   🔍 检测到复杂问题，启动长链推理...")
            reasoning_result = reasoning_agent.analyze(ticket, history)
            print(f"   📊 推理步骤数: {len(reasoning_result.get('reasoning_trace', []))}")
            print(f"   🎯 根因: {reasoning_result.get('root_cause', {}).get('cause', '未知')}")
        else:
            reasoning_result = {
                "need_human_escalation": False,
                "solution_path": [],
                "root_cause": {"severity": "low"}
            }
        
        # Step 4: 决策
        decision = decision_agent.decide(intent_result, reasoning_result, ticket)
        
        # Step 5: 输出结果
        print(format_output(decision))
    
    print("\n✅ 所有工单处理完成！")


if __name__ == "__main__":
    main()