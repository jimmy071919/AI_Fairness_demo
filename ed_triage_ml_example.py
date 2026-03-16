import logging
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("ED_Triage_ML")

def generate_synthetic_data(n_samples=2000):
    """
    產生虛擬的急診室數據。
    特徵包含：年齡、心跳、血壓、是否為弱勢群體 (0 或 1)。
    目標：是否為重症 (1: 重症入院, 0: 輕症回家)。
    在此設定弱勢群體的健康指標基準稍有不同，以模擬「資料分布的差異性 (Data Shift)」。
    """
    np.random.seed(42)
    
    # 70% 一般群體 (Majority), 30% 弱勢群體 (Minority)
    is_minority = np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3])
    
    age = np.random.normal(50, 15, size=n_samples)
    heart_rate = np.random.normal(80, 15, size=n_samples)
    blood_pressure = np.random.normal(120, 20, size=n_samples)
    
    # 真實狀況：年齡越大、心跳越快、血壓越高越危險
    # 假設：弱勢群體因日常缺乏照護，同樣指標下重症風險更高 (隱性特徵)
    risk_score = (age * 0.05 + heart_rate * 0.04 + blood_pressure * 0.02) - 10
    risk_score += is_minority * 2.5 # 弱勢群體有額外的風險基準值
    
    # 轉換為機率與標籤
    prob = 1 / (1 + np.exp(-risk_score))
    is_severe = (np.random.random(size=n_samples) < prob).astype(int)
    
    df = pd.DataFrame({
        'age': age,
        'heart_rate': heart_rate,
        'blood_pressure': blood_pressure,
        'is_minority': is_minority,
        'is_severe': is_severe
    })
    return df

class RepresentationLayer:
    def evaluate_fairness(self, data: pd.DataFrame):
        logger.info("\n--- [Representation Layer] 資料代表性分析 ---")
        majority_count = len(data[data['is_minority'] == 0])
        minority_count = len(data[data['is_minority'] == 1])
        logger.info(f"一般群體數量: {majority_count}, 弱勢群體數量: {minority_count}")
        
        majority_severe = data[data['is_minority'] == 0]['is_severe'].mean()
        minority_severe = data[data['is_minority'] == 1]['is_severe'].mean()
        logger.info(f"一般群體重症率: {majority_severe:.2%}, 弱勢群體重症率: {minority_severe:.2%}")

class LearningLayer:
    def train_model(self, X_train, y_train):
        logger.info("\n--- [Learning Layer] 訓練預測模型 ---")
        # 故意不將 'is_minority' 放入訓練特徵，模擬 Fairness Through Blindness (分配盲目)
        features = ['age', 'heart_rate', 'blood_pressure']
        model = LogisticRegression()
        model.fit(X_train[features], y_train)
        logger.info("模型訓練完成 (未包含敏感特徵 is_minority)")
        return model

class CalibrationLayer:
    def __init__(self, model):
        self.model = model
        
    def human_ai_collaboration_calibration(self, X_test: pd.DataFrame, y_test: pd.Series):
        logger.info("\n--- [Calibration Layer] 決策閾值校準 (Human-AI Collaboration) ---")
        features = ['age', 'heart_rate', 'blood_pressure']
        # 取得預測重症的機率
        probs = self.model.predict_proba(X_test[features])[:, 1]
        
        # 預設閾值: 0.5
        y_pred_default = (probs > 0.5).astype(int)
        
        logger.info(">> AI Agent (Surfacing): 發現預測結果存在偏差！")
        self._print_metrics(y_test, y_pred_default, X_test['is_minority'], "預設閾值 0.5")
        
        logger.info(">> AI Agent (Resolving): 提議對弱勢群體採取「放寬標準」的反事實測試 (Threshold = 0.4)...")
        y_pred_adjusted = y_pred_default.copy()
        # 針對弱勢群體，降低決策門檻 (0.4)
        minority_mask = (X_test['is_minority'] == 1)
        y_pred_adjusted[minority_mask] = (probs[minority_mask] > 0.4).astype(int)
        
        logger.info(">> Human Agent: 審查反事實測試結果。")
        self._print_metrics(y_test, y_pred_adjusted, X_test['is_minority'], "調整後閾值 (弱勢 0.4, 一般 0.5)")
        
        logger.info(">> Human Agent: 確認降低了偽陰性 (False Negative)，減少將重症弱勢病患趕回家的致命風險。核准政策更新！")

    def _print_metrics(self, y_true, y_pred, is_minority, policy_name):
        acc = accuracy_score(y_true, y_pred)
        logger.info(f"[{policy_name}] 整體準確率: {acc:.2%}")
        
        for group, name in [(0, "一般群體"), (1, "弱勢群體")]:
            mask = (is_minority == group)
            tn, fp, fn, tp = confusion_matrix(y_true[mask], y_pred[mask]).ravel()
            fn_rate = fn / (fn + tp) if (fn + tp) > 0 else 0
            logger.info(f"   - {name} 偽陰性率 (漏診率): {fn_rate:.2%}")


if __name__ == "__main__":
    logger.info("啟動 UV ML 整合範例 - FAIR 框架應用")
    
    # 1. 生成資料
    df = generate_synthetic_data()
    X = df[['age', 'heart_rate', 'blood_pressure', 'is_minority']]
    y = df['is_severe']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 2. Representation Layer
    rep_layer = RepresentationLayer()
    rep_layer.evaluate_fairness(df)
    
    # 3. Learning Layer
    learn_layer = LearningLayer()
    model = learn_layer.train_model(X_train, y_train)
    
    # 4. Calibration Layer
    calib_layer = CalibrationLayer(model)
    calib_layer.human_ai_collaboration_calibration(X_test, y_test)
