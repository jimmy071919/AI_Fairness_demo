import logging
from fair_framework import FAIRSystem, AIAgent, HumanAgent, RepresentationLayer, LearningLayer, CalibrationLayer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("ED_Triage")

# ==========================================
# 客製化急診分流 (ED Triage) 場景的代理人行為
# ==========================================

class EDTriageAIAgent(AIAgent):
    def surface(self, context):
        logger.info("[AI Agent] Surfacing: 持續掃描急診病患數據與模型預測偏差。")
        logger.warning("[AI Agent] 警告 (Surfacing): 發現特定高風險弱勢群體 (如高齡或偏鄉病患) 被誤判為輕症 (偽陰性率升高)！")
        return {"flagged_disparity": "High False Negative Rate for Elderly Patients"}

    def resolve(self, issues):
        logger.info("[AI Agent] Resolving: 運算多重公平性閾值調整與損失函數修正方案...")
        logger.info("[AI Agent] 提議 (Resolving): 降低該群體入院的決策閾值 5%，並附帶回溯策略 (Rollback parameters)。")
        return {"proposed_threshold_adjustment": -0.05, "rollback_ready": True}

class EDTriageHumanAgent(HumanAgent):
    def surface(self, context):
        logger.info("[Human Agent] Surfacing: 臨床委員會檢視 AI 提出的偏差警告。")
        logger.info("[Human Agent] 驗證 (Surfacing): 臨床醫師確認此偽陰性問題將導致嚴重生命危險，具備高度急迫性與重大性 (Materiality)。")
        return {"validated_severity": "CRITICAL"}

    def resolve(self, issues):
        logger.info("[Human Agent] Resolving: 評估 AI 閾值調整提案與醫院容積滿載 (Throughput) 之間的權衡 (Trade-offs)。")
        logger.info("[Human Agent] 裁決 (Resolving): 基於『臨床安全不容妥協』的底線，批准 AI 提出的降低閾值 5% 方案，並設定上線監控機制。")
        return {"decision": "APPROVED", "policy_updated": True}

# ==========================================
# 客製化 FAIR 系統，套用 ED Triage 代理人
# ==========================================

class EDTriageFAIRSystem(FAIRSystem):
    def __init__(self):
        super().__init__()
        # 將通用的代理人替換為 ED Triage 專用代理人 (展示 calibration layer 決策層次)
        self.calibration.ai_agent = EDTriageAIAgent()
        self.calibration.human_agent = EDTriageHumanAgent()

if __name__ == "__main__":
    logger.info(">>> 啟動 FAIR 框架：急診室 (ED) 檢傷分類場景演練 <<<")
    
    # 初始化急診分流 FAIR 系統
    ed_system = EDTriageFAIRSystem()
    
    # 模擬急診分流任務，這是一項高風險 (HIGH) 任務
    # 根據治理機制 (GR-2)，AI 只有提議權，必須經過人類「預先批准 (Preapproval)」
    task_data = {"patient_demographics": "mixed", "recent_drift": True}
    
    ed_system.execute_task(task_data=task_data, risk_level="HIGH")
    
    logger.info(">>> 演練結束：成功展示 Human-AI 協同機制的 Surfacing 與 Resolving 循環 <<<")
