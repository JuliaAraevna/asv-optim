"""
АСВ-ОПТИМ: риск-ориентированная прогнозно-аналитическая модель
выбора стратегии работы с активами ликвидируемых кредитных организаций.
"""

import pandas as pd


def calculate_er(strategy):
    """
    Расчёт ожидаемого чистого денежного результата (ER).
    ER = Σ(P_k * CF_k) - C
    """
    er = sum(p * cf for p, cf in strategy['scenarios']) - strategy['costs']
    return er


def calculate_enpv(strategy, r=0.15):
    """
    Расчёт ожидаемой приведённой стоимости (ENPV).
    ENPV = Σ[(CF_t - C_t) / (1 + r)^t]

    ВНИМАНИЕ: r = 0.15 — допущение (15% годовых).
    """
    enpv = 0
    for t, cf in enumerate(strategy['cash_flows']):
        cost_t = strategy['costs'] / len(strategy['cash_flows'])
        enpv += (cf - cost_t) / ((1 + r) ** t)
    return enpv


def compare_strategies(strategies, r=0.15):
    """
    Сравнение стратегий по ENPV.
    Возвращает DataFrame с результатами и лучшую стратегию.
    """
    results = []
    for name, strategy in strategies.items():
        er = calculate_er(strategy)
        enpv = calculate_enpv(strategy, r)
        results.append({
            'Стратегия': name,
            'ER, руб.': er,
            'ENPV, руб.': enpv
        })

    df = pd.DataFrame(results)
    df = df.sort_values('ENPV, руб.', ascending=False)
    best = df.iloc[0]['Стратегия']
    return df, best


# === ДЕМОНСТРАЦИОННЫЙ РАСЧЁТ ===
# Кейс: РосинтерБанк, право требования к ООО «Афганец»
# Номинал: 917 185 851 руб. — ФАКТ (судебный акт)
# Факт реализации: 52 000 000 руб. — ФАКТ (судебный акт)

asset = {
    'name': 'РосинтерБанк / Афганец',
    'nominal': 917_185_851
}

strategies = {
    'Реализация на торгах': {
        'costs': 137_577_878,
        'scenarios': [(0.3, 917_185_851), (0.7, 0)],
        'cash_flows': [0, 275_155_755]
    },
    'Публичное предложение': {
        'costs': 91_718_585,
        'scenarios': [(0.7, 52_000_000), (0.3, 0)],
        'cash_flows': [0, 52_000_000]
    },
    'Продолжение взыскания': {
        'costs': 183_437_170,
        'scenarios': [(0.4, 917_185_851), (0.6, 0)],
        'cash_flows': [0, 0, 366_874_340]
    },
    'Передача в отступное': {
        'costs': 45_859_293,
        'scenarios': [(0.5, 458_592_926), (0.5, 0)],
        'cash_flows': [0, 458_592_926]
    }
}

results, best = compare_strategies(strategies)

# === ВЫВОД РЕЗУЛЬТАТОВ ===
print(f"Актив: {asset['name']}")
print(f"Номинал: {asset['nominal']:,} руб.\n")
print(results.to_string(index=False))
print(f"\nЛучшая стратегия по ENPV: {best}")

# Экспорт в Excel
results.to_excel('asv_optim_results.xlsx', index=False)