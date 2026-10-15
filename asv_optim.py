"""
АСВ-ОПТИМ: риск-ориентированная прогнозно-аналитическая модель
выбора стратегии работы с активами ликвидируемых кредитных организаций.

Версия 2.0: поддержка загрузки активов из Excel-файла.
"""

import pandas as pd


# ============================================================
# РАСЧЁТНЫЕ ФУНКЦИИ
# ============================================================

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


# ============================================================
# ЗАГРУЗКА АКТИВОВ ИЗ EXCEL
# ============================================================

def load_assets_from_excel(file_path):
    """
    Загружает данные по активам из Excel-файла.
    
    Ожидаемая структура файла (лист «Активы»):
    | Актив | Стратегия | Расходы | Вероятность | Денежный поток | Срок (лет) |
    """
    df = pd.read_excel(file_path, sheet_name='Активы')
    assets = {}
    
    for _, row in df.iterrows():
        asset_name = row['Актив']
        if asset_name not in assets:
            assets[asset_name] = {
                'nominal': row.get('Номинал', 0),
                'strategies': {}
            }
        
        probability = row['Вероятность']
        cash_flow = row['Денежный поток']
        term = int(row['Срок (лет)'])
        
        assets[asset_name]['strategies'][row['Стратегия']] = {
            'costs': row['Расходы'],
            'scenarios': [(probability, cash_flow), (1 - probability, 0)],
            'cash_flows': [0] * (term - 1) + [cash_flow]
        }
    
    return assets


# ============================================================
# ОСНОВНАЯ ЛОГИКА
# ============================================================

def process_assets(assets, r=0.15):
    """
    Обрабатывает все активы и формирует итоговый отчёт.
    """
    all_results = []
    
    for asset_name, asset_data in assets.items():
        strategies = asset_data['strategies']
        df, best = compare_strategies(strategies, r)
        
        for _, row in df.iterrows():
            all_results.append({
                'Актив': asset_name,
                'Стратегия': row['Стратегия'],
                'ER, руб.': row['ER, руб.'],
                'ENPV, руб.': row['ENPV, руб.'],
                'Рекомендация': '← ЛУЧШАЯ' if row['Стратегия'] == best else ''
            })
    
    return pd.DataFrame(all_results)


# ============================================================
# ЗАПУСК
# ============================================================

if __name__ == '__main__':
    # Загрузка активов из Excel
    assets = load_assets_from_excel('input.xlsx')
    
    # Обработка всех активов
    results = process_assets(assets)
    
    # Вывод результатов
    print("=" * 70)
    print("АСВ-ОПТИМ: РЕЗУЛЬТАТЫ РАСЧЁТА")
    print("=" * 70)
    print(results.to_string(index=False))
    
    # Экспорт в Excel
    results.to_excel('asv_optim_results.xlsx', index=False)
    print("\nРезультаты сохранены в файл: asv_optim_results.xlsx")
