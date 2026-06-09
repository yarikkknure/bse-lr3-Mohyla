"""
Модуль: Калькулятор витрат на no-code проєкти
Автор: Могила Ярослав Романович, група ПЗПІ-25-4
Дисципліна: Основи програмної інженерії
ЛР 4: рефакторинг calc.py
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Final


# ── Перелік рівнів складності ─────────────────────────────────────────────────

class Complexity(IntEnum):
    LOW    = 1
    MEDIUM = 2
    HIGH   = 3


# ── Константи модуля ──────────────────────────────────────────────────────────

PLATFORM_RATES: Final[dict[str, int]] = {
    "Webflow": 800,
    "Bubble":  1200,
    "Glide":   600,
    "Make":    500,
}

COMPLEXITY_FACTORS: Final[dict[int, float]] = {
    Complexity.LOW:    1.0,
    Complexity.MEDIUM: 1.5,
    Complexity.HIGH:   2.5,
}

COMPLEXITY_LABELS: Final[dict[int, str]] = {
    Complexity.LOW:    "Низька",
    Complexity.MEDIUM: "Середня",
    Complexity.HIGH:   "Висока",
}

GUEST_LIMIT:  Final[int] = 3
REPORT_WIDTH: Final[int] = 50


# ── Структури даних ───────────────────────────────────────────────────────────

@dataclass
class CalculationRecord:
    """Один запис розрахунку вартості."""
    platforms:  list[str]
    complexity: int
    total_cost: float
    timestamp:  str


@dataclass
class User:
    """
    Користувач системи.

    Ролі:
    - Гість (is_registered=False): ліміт GUEST_LIMIT розрахунків.
    - Зареєстрований (is_registered=True): без ліміту, зберігається повна історія.
    """

    username:     str
    is_registered: bool = False
    history:      list[CalculationRecord] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.username or not isinstance(self.username, str):
            raise ValueError("username має бути непорожнім рядком.")

    @property
    def calculation_count(self) -> int:
        """Кількість виконаних розрахунків — завжди дорівнює len(history)."""
        return len(self.history)

    def can_calculate(self) -> bool:
        """
        True якщо користувач може виконати ще один розрахунок.
        Зареєстрований — завжди True.
        Гість — True поки calculation_count < GUEST_LIMIT.
        """
        if self.is_registered:
            return True
        return self.calculation_count < GUEST_LIMIT

    def add_to_history(self, record: CalculationRecord) -> None:
        """Зберігає запис розрахунку в history."""
        self.history.append(record)


# ── Бізнес-логіка ─────────────────────────────────────────────────────────────

def calculate_cost(platforms: list[str], complexity: int) -> float:
    """
    Розраховує вартість no-code проєкту.

    :param platforms: непорожній список платформ.
    :param complexity: рівень складності (1 — низька, 2 — середня, 3 — висока).
    :return: загальна вартість у USD.
    :raises ValueError: якщо complexity поза діапазоном, platforms порожній,
                        або зустрілась невідома платформа.
    """
    if complexity < 0:
        raise ValueError("Складність не може бути від'ємною.")
    if complexity not in COMPLEXITY_FACTORS:
        raise ValueError("Складність має бути від 1 до 3.")
    if not platforms:
        raise ValueError("Список платформ не може бути порожнім.")

    unknown = [p for p in platforms if p not in PLATFORM_RATES]
    if unknown:
        raise ValueError(f"Невідома платформа: {unknown}.")

    base_cost = sum(PLATFORM_RATES[p] for p in platforms)
    return base_cost * COMPLEXITY_FACTORS[complexity]


def generate_report(user: User) -> str:
    """
    Формує текстовий звіт по всіх розрахунках користувача.

    :param user: об'єкт User.
    :return: відформатований рядок звіту.
    """
    sep = "=" * REPORT_WIDTH
    user_type = "Зареєстрований" if user.is_registered else "Гість"

    lines = [
        sep,
        f"Користувач: {user.username}",
        f"Тип: {user_type}",
        sep,
    ]

    if not user.history:
        lines.append("Історія розрахунків відсутня.")
    else:
        for i, rec in enumerate(user.history, start=1):
            complexity_label = COMPLEXITY_LABELS.get(rec.complexity, str(rec.complexity))
            lines.append(f"Розрахунок #{i}")
            lines.append(f"  Платформи:  {', '.join(rec.platforms)}")
            lines.append(f"  Складність: {complexity_label}")
            lines.append(f"  Вартість:   {rec.total_cost:.2f} USD")
            lines.append(f"  Дата:       {rec.timestamp}")

    lines.append(sep)
    return "\n".join(lines)


def run_calculation(user: User, platforms: list[str], complexity: int) -> None:
    """
    Виконує розрахунок для користувача і зберігає результат в history.

    :param user: користувач.
    :param platforms: список платформ.
    :param complexity: рівень складності.
    """
    if not user.can_calculate():
        print("Ліміт вичерпано. Зареєструйтесь для необмеженого доступу.")
        return

    try:
        cost = calculate_cost(platforms, complexity)
    except ValueError as exc:
        print(f"Помилка вхідних даних: {exc}")
        return

    record = CalculationRecord(
        platforms=platforms,
        complexity=complexity,
        total_cost=cost,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    user.add_to_history(record)
    print(f"Вартість проєкту: {cost:.2f} USD")
