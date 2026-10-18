import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Настройки страницы
st.set_page_config(page_title="АСВ-ОПТИМ", page_icon="🏦", layout="centered")

st.title("🏦 АСВ-ОПТИМ")
st.markdown("**Интерактивный прототип прогнозно-аналитической модели** для оценки стратегий работы с активами.")

st.sidebar.header("Параметры актива")
nominal = st.sidebar.number_input("Номинал требования (руб.)", value=917185851, format="%d")
r_percent = st.sidebar.slider("Ставка дисконтирования (%)", min_value=5, max_value=30, value=15)
r = r_percent / 100

# Данные стратегий (ваши тестовые данные)
strategies = {
    'Реализация на торгах': {'costs': 137577878, 'scenarios': [(0.3, nominal), (0.7, 0)], 'cash_flows': [0, 275155755]},
    'Публичное предложение': {'costs': 91718585, 'scenarios': [(0.7, 52000000), (0.3, 0)], 'cash_flows': [0, 52000000]},
    'Продолжение взыскания': {'costs': 183437170, 'scenarios': [(0.4, nominal), (0.6, 0)], 'cash_flows': [0, 0, 366874340]},
    'Передача в отступное': {'costs': 45859293, 'scenarios': [(0.5, 458592926), (0.5, 0)], 'cash_flows': [0, 458592926]}
}

def calculate_er(strategy):
    return sum(p * cf for p, cf in strategy['scenarios']) - strategy['costs']

def calculate_enpv(strategy, r):
    enpv = 0
    for t, cf in enumerate(strategy['cash_flows']):
        cost_t = strategy['costs'] / len(strategy['cash_flows'])
        enpv += (cf - cost_t) / ((1 + r) ** t)
    return enpv

results = []
for name, strat in strategies.items():
    results.append({
        'Стратегия': name,
        'ER (руб.)': calculate_er(strat),
        'ENPV (руб.)': calculate_enpv(strat, r)
    })

df = pd.DataFrame(results).sort_values('ENPV (руб.)', ascending=False)

st.subheader("Результаты расчёта")
st.dataframe(df.style.format({'ER (руб.)': '{:,.0f}', 'ENPV (руб.)': '{:,.0f}'}), use_container_width=True)

best = df.iloc[0]['Стратегия']
st.success(f"✅ **Рекомендуемая стратегия:** {best} (максимальный ENPV)")

st.subheader("Сравнение стратегий по ENPV")
fig, ax = plt.subplots(figsize=(10, 4))
colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in df['ENPV (руб.)']]
bars = ax.barh(df['Стратегия'], df['ENPV (руб.)'], color=colors)
ax.set_xlabel("Ожидаемая приведенная стоимость (ENPV), руб.")
ax.invert_yaxis()

for bar in bars:
    width = bar.get_width()
    label_x_pos = width if width > 0 else width - 10000000
    ax.text(label_x_pos, bar.get_y() + bar.get_height()/2, f'{width:,.0f}', 
            va='center', ha='left' if width > 0 else 'right', fontsize=10)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
st.pyplot(fig)