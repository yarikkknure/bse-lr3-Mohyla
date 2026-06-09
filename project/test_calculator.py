"""
Файл модульних тестів: test_calculator.py
Проєкт: Калькулятор витрат на no-code проєкти
Автор: Могила Ярослав Романович, група ПЗПІ-25-4
ЛР 4: тести адаптовані після рефакторингу calc.py
Фреймворк: pytest
Техніки: Equivalence Partitioning (EP), Boundary Value Analysis (BVA)

Запуск:
    pytest test_calculator.py -v
    pytest test_calculator.py --cov=calc --cov-report=term -v
"""

import pytest
from calc import (
    User,
    CalculationRecord,
    calculate_cost,
    generate_report,
    run_calculation,
    GUEST_LIMIT,
)

# Допоміжний запис для тестів
_SAMPLE_RECORD = CalculationRecord(
    platforms=["Webflow"],
    complexity=1,
    total_cost=800.0,
    timestamp="2026-06-03 12:00:00",
)


def _add_records(user: User, count: int) -> None:
    """Додає count записів у history через публічний API."""
    for _ in range(count):
        user.add_to_history(_SAMPLE_RECORD)


# ===================================================================
class TestUserInit:
    """Тести ініціалізації об'єкта User."""

    def test_guest_default_attributes(self):
        """
        TC-01 | EP: допустимий username, is_registered=False (за замовч.)
        Очікується: усі атрибути встановлено коректно.
        """
        user = User(username="guest")
        assert user.username == "guest"
        assert user.is_registered is False
        assert user.history == []
        assert user.calculation_count == 0

    def test_registered_user_flag_is_true(self):
        """
        TC-02 | EP: is_registered=True
        Очікується: is_registered == True.
        """
        user = User(username="yaroslav", is_registered=True)
        assert user.is_registered is True

    def test_empty_username_raises(self):
        """
        TC-03 | EP: порожній рядок username → ValueError.
        """
        with pytest.raises(ValueError):
            User(username="")

    def test_non_string_username_raises(self):
        """
        TC-04 | EP: username не є рядком (None) → ValueError.
        """
        with pytest.raises(ValueError):
            User(username=None)


# ===================================================================
class TestUserCanCalculate:
    """Тести методу can_calculate з EP та BVA на межі GUEST_LIMIT=3."""

    def test_guest_count_0_can_calculate(self):
        """
        TC-05 | BVA: гість, count=0 (нижня межа) → True.
        """
        user = User("guest")
        assert user.can_calculate() is True

    def test_guest_count_1_can_calculate(self):
        """
        TC-06 | BVA: гість, count=1 (межа+1) → True.
        """
        user = User("guest")
        _add_records(user, 1)
        assert user.can_calculate() is True

    def test_guest_count_2_can_calculate(self):
        """
        TC-07 | BVA: гість, count=2 (ліміт-1) → True.
        """
        user = User("guest")
        _add_records(user, 2)
        assert user.can_calculate() is True

    def test_guest_count_3_cannot_calculate(self):
        """
        TC-08 | BVA: гість, count=3 (рівно ліміт) → False.
        """
        user = User("guest")
        _add_records(user, GUEST_LIMIT)
        assert user.can_calculate() is False

    def test_guest_count_4_cannot_calculate(self):
        """
        TC-09 | BVA: гість, count=4 (понад ліміт) → False.
        """
        user = User("guest")
        _add_records(user, 4)
        assert user.can_calculate() is False

    def test_registered_any_count_can_calculate(self):
        """
        TC-10 | EP: зареєстрований, багато записів → True (без ліміту).
        """
        user = User("yaroslav", is_registered=True)
        _add_records(user, 10)
        assert user.can_calculate() is True


class TestUserAddToHistory:
    """Тести методу add_to_history."""

    def test_add_single_record_increments_count(self):
        """
        TC-11 | Позитивний: додавання одного запису → count=1, len(history)=1.
        """
        user = User("yaroslav", is_registered=True)
        record = CalculationRecord(
            platforms=["Webflow"],
            complexity=1,
            total_cost=800.0,
            timestamp="2026-06-03 12:00:00",
        )
        user.add_to_history(record)
        assert user.calculation_count == 1
        assert len(user.history) == 1

    def test_add_two_records_count_is_2(self):
        """
        TC-12 | Позитивний: два записи → count=2, history[1].total_cost коректна.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history(CalculationRecord(["Webflow"], 1, 800.0,  "2026-06-03"))
        user.add_to_history(CalculationRecord(["Bubble"],  2, 1800.0, "2026-06-03"))
        assert user.calculation_count == 2
        assert user.history[1].total_cost == 1800.0

    def test_add_record_stores_correct_data(self):
        """
        TC-13 | Позитивний: дані запису зберігаються без змін.
        """
        user = User("yaroslav", is_registered=True)
        record = CalculationRecord(["Glide", "Make"], 3, 2750.0, "2026-06-03")
        user.add_to_history(record)
        assert user.history[0].platforms == ["Glide", "Make"]
        assert user.history[0].total_cost == 2750.0


class TestCalculateCost:
    """
    Тести функції calculate_cost.
    EP-класи для platforms: порожній / одна відома / кілька / невідома.
    EP-класи для complexity: від'ємне / 0 / 1..3 / >3.
    BVA на межах complexity: 0, 1, 3, 4.
    """

    # --- EP: від'ємна складність ---
    def test_negative_complexity_raises(self):
        """TC-14 | EP: complexity=-1 → ValueError('від'ємною')."""
        with pytest.raises(ValueError, match="від'ємною"):
            calculate_cost(["Webflow"], -1)

    # --- BVA: complexity=0 ---
    def test_complexity_0_raises(self):
        """TC-15 | BVA: complexity=0 → ValueError('від 1 до 3')."""
        with pytest.raises(ValueError, match="від 1 до 3"):
            calculate_cost(["Webflow"], 0)

    # --- BVA: complexity=4 ---
    def test_complexity_4_raises(self):
        """TC-16 | BVA: complexity=4 → ValueError('від 1 до 3')."""
        with pytest.raises(ValueError, match="від 1 до 3"):
            calculate_cost(["Webflow"], 4)

    # --- EP: порожній список ---
    def test_empty_platforms_raises(self):
        """TC-17 | EP: platforms=[] → ValueError('порожнім')."""
        with pytest.raises(ValueError, match="порожнім"):
            calculate_cost([], 1)

    # --- EP: невідома платформа ---
    def test_unknown_platform_raises(self):
        """TC-18 | EP: platform='WordPress' → ValueError('Невідома')."""
        with pytest.raises(ValueError, match="Невідома"):
            calculate_cost(["WordPress"], 1)

    # --- BVA: complexity=1 ---
    def test_webflow_complexity_1(self):
        """TC-19 | BVA: Webflow, complexity=1 → 800*1.0=800.0."""
        assert calculate_cost(["Webflow"], 1) == 800.0

    # --- EP: complexity=2 ---
    def test_bubble_complexity_2(self):
        """TC-20 | EP: Bubble, complexity=2 → 1200*1.5=1800.0."""
        assert calculate_cost(["Bubble"], 2) == 1800.0

    # --- BVA: complexity=3 ---
    def test_glide_complexity_3(self):
        """TC-21 | BVA: Glide, complexity=3 → 600*2.5=1500.0."""
        assert calculate_cost(["Glide"], 3) == 1500.0

    # --- EP: Make ---
    def test_make_complexity_1(self):
        """TC-22 | EP: Make, complexity=1 → 500*1.0=500.0."""
        assert calculate_cost(["Make"], 1) == 500.0

    # --- EP: кілька платформ ---
    def test_webflow_bubble_complexity_2(self):
        """TC-23 | EP: Webflow+Bubble, complexity=2 → (800+1200)*1.5=3000.0."""
        assert calculate_cost(["Webflow", "Bubble"], 2) == 3000.0

    # --- EP: всі платформи ---
    def test_all_platforms_complexity_3(self):
        """TC-24 | EP: всі 4 платформи, complexity=3 → (800+1200+600+500)*2.5=7750.0."""
        assert calculate_cost(["Webflow", "Bubble", "Glide", "Make"], 3) == 7750.0

    # --- EP: Bubble+Make ---
    def test_bubble_make_complexity_1(self):
        """TC-25 | EP: Bubble+Make, complexity=1 → (1200+500)*1.0=1700.0."""
        assert calculate_cost(["Bubble", "Make"], 1) == 1700.0


class TestGenerateReport:
    """Тести функції generate_report."""

    def test_empty_history_returns_absence_message(self):
        """
        TC-26 | EP: порожня history → рядок 'Історія розрахунків відсутня'.
        """
        user = User("guest")
        report = generate_report(user)
        assert "Історія розрахунків відсутня" in report

    def test_report_contains_username(self):
        """
        TC-27 | Позитивний: звіт містить ім'я користувача.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history(CalculationRecord(["Webflow"], 1, 800.0, "2026-06-03"))
        report = generate_report(user)
        assert "yaroslav" in report

    def test_report_contains_total_cost(self):
        """
        TC-28 | Позитивний: звіт містить відформатовану суму.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history(CalculationRecord(["Bubble"], 2, 1800.0, "2026-06-03"))
        report = generate_report(user)
        assert "1800.00" in report

    def test_report_guest_type_label(self):
        """
        TC-29 | EP: гість → 'Гість' у звіті.
        """
        user = User("guest_user", is_registered=False)
        user.add_to_history(CalculationRecord(["Make"], 1, 500.0, "2026-06-03"))
        report = generate_report(user)
        assert "Гість" in report

    def test_report_registered_type_label(self):
        """
        TC-30 | EP: зареєстрований → 'Зареєстрований' у звіті.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history(CalculationRecord(["Glide"], 3, 1500.0, "2026-06-03"))
        report = generate_report(user)
        assert "Зареєстрований" in report

    def test_report_multiple_records_count(self):
        """
        TC-31 | Позитивний: звіт з двома записами містить '#1' та '#2'.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history(CalculationRecord(["Webflow"], 1, 800.0,  "2026-06-03"))
        user.add_to_history(CalculationRecord(["Bubble"],  2, 1800.0, "2026-06-03"))
        report = generate_report(user)
        assert "Розрахунок #1" in report
        assert "Розрахунок #2" in report

    def test_report_complexity_label_low(self):
        """
        TC-32 | EP: complexity=1 → 'Низька' у звіті.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history(CalculationRecord(["Make"], 1, 500.0, "2026-06-03"))
        report = generate_report(user)
        assert "Низька" in report

    def test_report_complexity_label_high(self):
        """
        TC-33 | EP: complexity=3 → 'Висока' у звіті.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history(CalculationRecord(["Glide"], 3, 1500.0, "2026-06-03"))
        report = generate_report(user)
        assert "Висока" in report


class TestRunCalculation:
    """Тести функції run_calculation."""

    def test_successful_calculation_adds_to_history(self):
        """
        TC-34 | Позитивний: дозволений розрахунок → запис у history, count=1.
        """
        user = User("yaroslav", is_registered=True)
        run_calculation(user, ["Webflow"], 1)
        assert user.calculation_count == 1
        assert user.history[0].total_cost == 800.0

    def test_guest_within_limit_calculates(self):
        """
        TC-35 | EP: гість, count=0 < 3 → розрахунок виконується.
        """
        user = User("guest")
        run_calculation(user, ["Make"], 2)
        assert user.calculation_count == 1

    def test_guest_at_limit_blocked(self, capsys):
        """
        TC-36 | BVA: гість, count=3 (ліміт) → розрахунок заблокований,
        history не змінюється, виводиться повідомлення про ліміт.
        """
        user = User("guest")
        _add_records(user, GUEST_LIMIT)
        run_calculation(user, ["Webflow"], 1)
        assert user.calculation_count == GUEST_LIMIT
        assert len(user.history) == GUEST_LIMIT
        captured = capsys.readouterr()
        assert "Ліміт вичерпано" in captured.out

    def test_calculation_stores_correct_platform_and_complexity(self):
        """
        TC-37 | Позитивний: запис містить правильні платформи та складність.
        """
        user = User("yaroslav", is_registered=True)
        run_calculation(user, ["Bubble", "Glide"], 3)
        rec = user.history[0]
        assert rec.platforms == ["Bubble", "Glide"]
        assert rec.complexity == 3
        assert rec.total_cost == (1200 + 600) * 2.5

    def test_three_consecutive_guest_calculations(self):
        """
        TC-38 | BVA: гість виконує рівно 3 розрахунки (весь ліміт) → усі проходять.
        """
        user = User("guest")
        run_calculation(user, ["Webflow"], 1)
        run_calculation(user, ["Make"],    1)
        run_calculation(user, ["Glide"],   1)
        assert user.calculation_count == 3

    def test_fourth_guest_calculation_blocked(self):
        """
        TC-39 | BVA: четвертий розрахунок гостя → заблокований, count залишається 3.
        """
        user = User("guest")
        run_calculation(user, ["Webflow"], 1)
        run_calculation(user, ["Make"],    1)
        run_calculation(user, ["Glide"],   1)
        run_calculation(user, ["Bubble"],  2)   # 4-й — заблокований
        assert user.calculation_count == 3
