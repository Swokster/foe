from collections import Counter
import itertools
import os
from typing import List, Tuple
import streamlit as st

BUILDINGS = {
    "БЛ": {
        "type": "percent",
        "value": 15,
        "name": "Базовый лагерь",
        "img": "bc.png",
    },
    "ОЛ": {
        "type": "percent",
        "value": 30,
        "name": "Обычный лагерь",
        "img": "rc.png",
    },
    "УЛ": {
        "type": "percent",
        "value": 100,
        "name": "Улучшенный лагерь",
        "img": "ac.png",
    },
    "БА": {
        "type": "absolute",
        "value": 25,
        "name": "Базовый Аванпост",
        "img": "ba.png",
    },
    "ОА": {
        "type": "absolute",
        "value": 50,
        "name": "Обычный Аванпост",
        "img": "ra.png",
    },
    "УА": {
        "type": "absolute",
        "value": 100,
        "name": "Улучшенный Аванпост",
        "img": "aa.png",
    },
}

EMPTY_IMG = "na.png"


def generate_combinations_with_replacement(
    building_keys: List[str], Y: int
) -> List[Tuple]:
  all_combinations = []
  for r in range(1, Y + 1):
    for combo in itertools.combinations_with_replacement(building_keys, r):
      all_combinations.append(combo)
  return all_combinations


def calculate_combinations(
    X: int, A: int, B: int, Y: int, castle_bonus: float
) -> List[Tuple]:
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

    # Итоговое значение с учетом бонуса замка
    total = round(
        (X + A + sum_abs) * (1 + (B + sum_percent) / 100)
        + (A + sum_abs) * (castle_bonus)
    )
    formula_str = (
        f"({X} + {A} + {sum_abs}) * (1 + ({B} + {sum_percent})/100) +"
        f" ({A} + {sum_abs}) * ({castle_bonus} - 1)"
    )

    counter = Counter(combo)
    compact_parts = []
    for key, count in counter.items():
      if count > 1:
        compact_parts.append(f"{count}×{BUILDINGS[key]['name']}")
      else:
        compact_parts.append(BUILDINGS[key]["name"])
    compact_str = " + ".join(compact_parts)

    bonuses_str = f"Абс: +{sum_abs} | Проц: +{round(sum_percent)}%"
    results.append((compact_str, bonuses_str, formula_str, total, combo, Y))

  results.sort(key=lambda x: x[3], reverse=True)
  return results


def main():
  st.set_page_config(
      page_title="Калькулятор строений", page_icon="🏗️", layout="centered"
  )

  st.title("Калькулятор бонусов осадных строений")

  st.markdown(
      """
    <style>
    .footer {
        text-align: center;
        color: #888888;
        font-size: 13px;
        margin-top: 50px;
        margin-bottom: 20px;
        border-top: 1px solid #e0e0e0;
        padding-top: 15px;
    }
    </style>
    """,
      unsafe_allow_html=True,
  )

  col1, col2, col3, col4, col5 = st.columns(5)
  with col1:
    X_input = st.number_input(
        "База",
        value=None,
        step=1,
        format="%d",
        help="Базовое значение показателя без учета бонусов",
    )
  with col2:
    A_input = st.number_input(
        "Абс. бонус",
        value=None,
        step=1,
        format="%d",
        help="Абсолютные бонусы от стоящих строений",
    )
    A = int(A_input) if A_input is not None else 0
  with col3:
    B_input = st.number_input(
        "Проц. бонус",
        value=None,
        step=1,
        format="%d",
        help="Процентные бонусы от стоящих строений",
    )
    B = int(B_input) if B_input is not None else 0
  with col4:
      castle_option = st.selectbox(
          "Бонус замка",
          ["нет 0%", "Базовый 25%", "Обычный 50%", "Улучшенный 100%"],
          index=3,
          help="Бонус замка к абсолютным показателям",
      )
      castle_map = {
          "Нет": 0.0,
          "Базовый 25%": 0.25,
          "Обычный 50%": 0.5,
          "Улучшенный 100%": 1.0,
      }
      castle_bonus = castle_map[castle_option]
  with col5:
      Y = st.selectbox(
          "Количество",
          [1, 2, 3],
          index=2,
          help="Максимальное количество свободных для постройки зданий",
      )

  st.markdown("---")

  if X_input is None:
    st.info("Пожалуйста, введите базовое значение сектора")

    with st.container(border=True):
      st.markdown("**#1 Ожидание ввода базы...**")
      cols = st.columns([1, 1, 1, 2])
      for idx in range(3):
        with cols[idx]:
          if os.path.exists(EMPTY_IMG):
            st.image(EMPTY_IMG, width=75)
          else:
            st.image("https://placehold.co/75x75?text=NA", width=75)
      with cols[3]:
        st.markdown("**Бонусы:**  \nАбс: +0 | Проц: +0%")
        st.metric("Итог", "0")
  else:
    X = int(X_input)
    results = calculate_combinations(X, A, B, Y, castle_bonus)
    if not results:
      st.warning("Нет доступных комбинаций.")
    else:
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

      for i, (compact_str, bonuses, formula, total, combo, max_slots) in (
          enumerate(display_results, 1)
      ):
        with st.container(border=True):
          st.markdown(f"**#{i} {compact_str}**")

          cols = st.columns([1, 1, 1, 2])

          padded_combo = list(combo)
          while len(padded_combo) < 3:
            padded_combo.insert(0, None)

          for idx in range(3):
            with cols[idx]:
              building_key = padded_combo[idx]
              if building_key is None:
                img_path = EMPTY_IMG
              else:
                img_path = BUILDINGS[building_key]["img"]

              if os.path.exists(img_path):
                st.image(img_path, width=75)
              else:
                st.image("https://placehold.co/75x75?text=NA", width=75)

          with cols[3]:
            st.markdown(f"**Бонусы:**  \n{bonuses}")
            # Выводим итог как целое число без знаков после запятой
            st.metric("Итог", f"{int(total)}")

  st.markdown(
      "<div class='footer'>Powered by Swokster 2026</div>",
      unsafe_allow_html=True,
  )



if __name__ == "__main__":
  main()