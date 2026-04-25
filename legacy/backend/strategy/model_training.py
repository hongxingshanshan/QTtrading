import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def generate_label(df, n_days_ahead=5):
    """生成未来收益率标签"""
    df = df.copy()
    df['future_return'] = df.groupby('ts_code')['close'].shift(-n_days_ahead) / df['close'] - 1
    df['label'] = (df['future_return'] > 0).astype(int)
    return df.dropna(subset=['label'])

def train_ml_model(df, features, label_col='label', model_path='models/lgb_model.pkl'):
    """训练 LightGBM 模型并返回训练结果"""
    X = df[features]
    y = df[label_col]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    clf = lgb.LGBMClassifier(n_estimators=100, max_depth=5)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    print(f"模型准确率: {acc:.4f}")
    print("分类报告：\n", report)

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(clf, model_path)
    print(f"模型已保存至: {model_path}")

    return clf

def generate_signal(df, features, model, threshold=0.6):
    """生成上涨概率预测信号"""
    df = df.copy()
    X = df[features]
    df['pred_proba'] = model.predict_proba(X)[:, 1]
    df['signal'] = (df['pred_proba'] > threshold).astype(int)
    return df

if __name__ == "__main__":
    # 载入打分后的因子数据（注意你需要替换为自己的路径）
    df = pd.read_csv('data/factor_score.csv')

    # 选择标准化后的因子名
    features = ['factor1_norm', 'factor2_norm', 'factor3_norm']  # 修改为你的因子名

    # 步骤 1: 构造标签
    df = generate_label(df, n_days_ahead=5)

    # 步骤 2: 训练模型
    clf = train_ml_model(df, features, model_path='models/lgb_model.pkl')

    # 步骤 3: 生成预测信号
    df = generate_signal(df, features, clf, threshold=0.6)

    # 保存包含信号的结果
    df.to_csv('output/df_with_signals.csv', index=False)
    print("信号文件已保存：output/df_with_signals.csv")
