from collections import Counter
import itertools
from typing import List, Tuple
import streamlit as st

# Конфигурация строений
BUILDINGS = {
    "БЛ": {"type": "percent", "value": 15, "name": "Базовый лагерь"},
    "ОЛ": {"type": "percent", "value": 30, "name": "Обычный лагерь"},
    "УЛ": {"type": "percent", "value": 100, "name": "Улучшенный лагерь"},
    "БА": {"type": "absolute", "value": 25, "name": "Базовый Аванпост"},
    "ОА": {"type": "absolute", "value": 50, "name": "Обычный Аванпост"},
    "УА": {"type": "absolute", "value": 100, "name": "Улучшенный Аванпост"},
}


def generate_combinations_with_replacement(
    building_keys: List[str], Y: int
) -> List[Tuple]:
  all_combinations = []
  for r in range(1, Y + 1):
    for combo in itertools.combinations_with_replacement(building_keys, r):
      all_combinations.append(combo)
  return all_combinations


def calculate_combinations(X: float, A: float, B: float, Y: int) -> List[Tuple]:
  results = []
  building_keys = list(BUILDINGS.keys())
  all_combinations = generate_combinations_with_replacement(building_keys, Y)

  for combo in all_combinations:
    sum_abs = sum(
        BUILDINGS[b]["value"] for b in combo if BUILDINGS[b]["type"] == "absolute"
    )
    sum_percent = sum(
        BUILDINGS[b]["value"] for b in combo if BUILDINGS[b]["type"] == "percent"
    )

    total = (X + A + sum_abs) * (1 + (B + sum_percent) / 100)
    formula_str = (
        f"({X} + {A} + {sum_abs}) * (1 + ({B} + {sum_percent})/100)"
    )

    names = [BUILDINGS[b]["name"] for b in combo]
    buildings_str = " + ".join(names)

    counter = Counter(combo)
    compact_parts = []
    for key, count in counter.items():
      if count > 1:
        compact_parts.append(f"{count}×{BUILDINGS[key]['name']}")
      else:
        compact_parts.append(BUILDINGS[key]["name"])
    compact_str = " + ".join(compact_parts)

    bonuses_str = f"Абс: +{sum_abs} | Проц: +{sum_percent}%"
    results.append(
        (compact_str, buildings_str, bonuses_str, formula_str, total, combo)
    )

  results.sort(key=lambda x: x[4], reverse=True)
  return results


def main():
  st.set_page_config(
      page_title="Калькулятор строений", page_icon="🏗️", layout="centered"
  )

  st.title("️Калькулятор бонусов осадных строений")

  # Компактный ввод параметров в одну строку (в колонках)
  col1, col2, col3, col4 = st.columns(4)
  with col1:
    X = st.number_input("База (X)", value=0, step=1.0)
  with col2:
    A = st.number_input("Абс. (A)", value=0, step=1.0)
  with col3:
    B = st.number_input("Проц. (B)", value=0, step=1.0)
  with col4:
    Y = st.selectbox("Зданий (Y)", [1, 2, 3], index=1)

  st.markdown("---")

  # Расчет
  results = calculate_combinations(X, A, B, Y)
  if not results:
    st.warning("Нет доступных комбинаций.")
    return

  # Главный результат
  best = results[0]
  st.success(f"🏆 **Лучший набор:** {best[0]} — **{best[4]:.2f}**")

  # Настройка отображения списка
  cols_top = st.columns([2, 2])
  with cols_top[0]:
    limit_option = st.selectbox(
        "Показывать", ["Топ 3", "Топ 5", "Топ 10", "Все"], index=0
    )
  with cols_top[1]:
    st.markdown(
        f"<p style='text-align: right; padding-top: 25px; color:"
        f" gray;'>Комбинаций: {len(results)}</p>",
        unsafe_allow_html=True,
    )

  limit_map = {"Топ 3": 3, "Топ 5": 5, "Топ 10": 10, "Все": len(results)}
  display_results = results[: limit_map[limit_option]]

  # Таблица результатов
  for i, (compact_str, full_str, bonuses, formula, total, _) in enumerate(
      display_results, 1
  ):
    with st.container(border=True):
      c1, c2, c3 = st.columns([3, 2, 1])
      with c1:
        st.markdown(f"**#{i} {compact_str}**")
        st.caption(f"Формула: `{formula}`")
      with c2:
        st.text(bonuses)
      with c3:
        st.metric("Итог", f"{total:.2f}")


if __name__ == "__main__":
  main()