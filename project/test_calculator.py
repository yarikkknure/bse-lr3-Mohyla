"""
Файл модульних тестів: test_calculator.py
Проєкт: Калькулятор витрат на no-code проєкти
Автор: Могила Ярослав Романович, група ПЗПІ-25-4
Фреймворк: pytest
Техніки: Equivalence Partitioning (EP), Boundary Value Analysis (BVA)

Запуск:
    pytest test_calculator.py -v
    pytest test_calculator.py --cov=calc --cov-report=term -v
"""

import pytest
from calc import User, ProjectCalculator, run_calculation


# ===================================================================
# БЛОК 1 — Клас User: конструктор (__init__)
# ===================================================================

class TestUserInit:
    """Тести ініціалізації об'єкта User."""

    def test_guest_default_attributes(self):
        """
        TC-01 | EP: допустимий username, is_registered=False (за замовч.)
        Очікується: усі атрибути встановлено коректно.
        """
        # Arrange / Act
        user = User(username="guest")
        # Assert
        assert user.username == "guest"
        assert user.is_registered is False
        assert user.calculation_history == []
        assert user.calculation_count == 0

    def test_registered_user_flag_is_true(self):
        """
        TC-02 | EP: is_registered=True
        Очікується: is_registered == True.
        """
        # Arrange / Act
        user = User(username="yaroslav", is_registered=True)
        # Assert
        assert user.is_registered is True

    def test_empty_username_raises(self):
        """
        TC-03 | EP: порожній рядок username → ValueError.
        """
        # Arrange / Act / Assert
        with pytest.raises(ValueError):
            User(username="")

    def test_non_string_username_raises(self):
        """
        TC-04 | EP: username не є рядком (None) → ValueError.
        """
        with pytest.raises(ValueError):
            User(username=None)


# ===================================================================
# БЛОК 2 — User.can_calculate(): ліміт гостя та права зареєстрованого
# ===================================================================

class TestUserCanCalculate:
    """Тести методу can_calculate з EP та BVA на межі GUEST_LIMIT=3."""

    def test_guest_count_0_can_calculate(self):
        """
        TC-05 | BVA: гість, count=0 (нижня межа) → True.
        """
        # Arrange
        user = User("guest")
        # Act / Assert
        assert user.can_calculate() is True

    def test_guest_count_1_can_calculate(self):
        """
        TC-06 | BVA: гість, count=1 (межа+1) → True.
        """
        user = User("guest")
        user.calculation_count = 1
        assert user.can_calculate() is True

    def test_guest_count_2_can_calculate(self):
        """
        TC-07 | BVA: гість, count=2 (ліміт-1) → True.
        """
        user = User("guest")
        user.calculation_count = 2
        assert user.can_calculate() is True

    def test_guest_count_3_cannot_calculate(self):
        """
        TC-08 | BVA: гість, count=3 (рівно ліміт) → False.
        """
        user = User("guest")
        user.calculation_count = 3
        assert user.can_calculate() is False

    def test_guest_count_4_cannot_calculate(self):
        """
        TC-09 | BVA: гість, count=4 (понад ліміт) → False.
        """
        user = User("guest")
        user.calculation_count = 4
        assert user.can_calculate() is False

    def test_registered_any_count_can_calculate(self):
        """
        TC-10 | EP: зареєстрований, count=999 → True (без ліміту).
        """
        user = User("yaroslav", is_registered=True)
        user.calculation_count = 999
        assert user.can_calculate() is True


# ===================================================================
# БЛОК 3 — User.add_to_history()
# ===================================================================

class TestUserAddToHistory:
    """Тести методу add_to_history."""

    def test_add_single_record_increments_count(self):
        """
        TC-11 | Позитивний: додавання одного запису → count=1, len(history)=1.
        """
        # Arrange
        user = User("yaroslav", is_registered=True)
        record = {
            "platforms": ["Webflow"],
            "complexity": 1,
            "total_cost": 800.0,
            "timestamp": "2026-06-03 12:00:00",
        }
        # Act
        user.add_to_history(record)
        # Assert
        assert user.calculation_count == 1
        assert len(user.calculation_history) == 1

    def test_add_two_records_count_is_2(self):
        """
        TC-12 | Позитивний: два записи → count=2, history[1].total_cost коректна.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history({"platforms": ["Webflow"], "complexity": 1,
                              "total_cost": 800.0, "timestamp": "2026-06-03"})
        user.add_to_history({"platforms": ["Bubble"], "complexity": 2,
                              "total_cost": 1800.0, "timestamp": "2026-06-03"})
        assert user.calculation_count == 2
        assert user.calculation_history[1]["total_cost"] == 1800.0

    def test_add_record_stores_correct_data(self):
        """
        TC-13 | Позитивний: дані запису зберігаються без змін.
        """
        user = User("yaroslav", is_registered=True)
        record = {"platforms": ["Glide", "Make"], "complexity": 3,
                  "total_cost": 2750.0, "timestamp": "2026-06-03"}
        user.add_to_history(record)
        assert user.calculation_history[0]["platforms"] == ["Glide", "Make"]
        assert user.calculation_history[0]["total_cost"] == 2750.0


# ===================================================================
# БЛОК 4 — ProjectCalculator.calculate_cost()
# ===================================================================

class TestCalculateCost:
    """
    Тести методу calculate_cost.
    EP-класи для platforms_list: порожній / одна відома / кілька / невідома.
    EP-класи для complexity: від'ємне / 0 / 1..3 / >3.
    BVA на межах complexity: 0, 1, 3, 4.
    """

    @pytest.fixture
    def calc(self):
        return ProjectCalculator()

    # --- EP: від'ємна складність ---
    def test_negative_complexity_raises(self, calc):
        """TC-14 | EP: complexity=-1 → ValueError('від'ємною')."""
        with pytest.raises(ValueError, match="від'ємною"):
            calc.calculate_cost(["Webflow"], -1)

    # --- BVA: complexity=0 (нижня межа поза діапазоном) ---
    def test_complexity_0_raises(self, calc):
        """TC-15 | BVA: complexity=0 → ValueError('від 1 до 3')."""
        with pytest.raises(ValueError, match="від 1 до 3"):
            calc.calculate_cost(["Webflow"], 0)

    # --- BVA: complexity=4 (верхня межа поза діапазоном) ---
    def test_complexity_4_raises(self, calc):
        """TC-16 | BVA: complexity=4 → ValueError('від 1 до 3')."""
        with pytest.raises(ValueError, match="від 1 до 3"):
            calc.calculate_cost(["Webflow"], 4)

    # --- EP: порожній список платформ ---
    def test_empty_platforms_raises(self, calc):
        """TC-17 | EP: platforms_list=[] → ValueError('порожнім')."""
        with pytest.raises(ValueError, match="порожнім"):
            calc.calculate_cost([], 1)

    # --- EP: невідома платформа ---
    def test_unknown_platform_raises(self, calc):
        """TC-18 | EP: platform='WordPress' → ValueError('Невідома')."""
        with pytest.raises(ValueError, match="Невідома"):
            calc.calculate_cost(["WordPress"], 1)

    # --- BVA: complexity=1 (нижня допустима межа) ---
    def test_webflow_complexity_1(self, calc):
        """TC-19 | BVA: Webflow, complexity=1 → 800*1.0=800.0."""
        # Arrange / Act
        result = calc.calculate_cost(["Webflow"], 1)
        # Assert
        assert result == 800.0

    # --- EP: complexity=2 (середнє значення) ---
    def test_bubble_complexity_2(self, calc):
        """TC-20 | EP: Bubble, complexity=2 → 1200*1.5=1800.0."""
        result = calc.calculate_cost(["Bubble"], 2)
        assert result == 1800.0

    # --- BVA: complexity=3 (верхня допустима межа) ---
    def test_glide_complexity_3(self, calc):
        """TC-21 | BVA: Glide, complexity=3 → 600*2.5=1500.0."""
        result = calc.calculate_cost(["Glide"], 3)
        assert result == 1500.0

    # --- EP: платформа Make ---
    def test_make_complexity_1(self, calc):
        """TC-22 | EP: Make, complexity=1 → 500*1.0=500.0."""
        result = calc.calculate_cost(["Make"], 1)
        assert result == 500.0

    # --- EP: кілька платформ ---
    def test_webflow_bubble_complexity_2(self, calc):
        """TC-23 | EP: Webflow+Bubble, complexity=2 → (800+1200)*1.5=3000.0."""
        result = calc.calculate_cost(["Webflow", "Bubble"], 2)
        assert result == 3000.0

    # --- EP: всі чотири платформи ---
    def test_all_platforms_complexity_3(self, calc):
        """TC-24 | EP: всі 4 платформи, complexity=3 → (800+1200+600+500)*2.5=7750.0."""
        result = calc.calculate_cost(["Webflow", "Bubble", "Glide", "Make"], 3)
        assert result == 7750.0

    # --- EP: одна платформа, validity перевірка всіх тарифів ---
    def test_bubble_make_complexity_1(self, calc):
        """TC-25 | EP: Bubble+Make, complexity=1 → (1200+500)*1.0=1700.0."""
        result = calc.calculate_cost(["Bubble", "Make"], 1)
        assert result == 1700.0


# ===================================================================
# БЛОК 5 — ProjectCalculator.generate_report()
# ===================================================================

class TestGenerateReport:
    """Тести методу generate_report."""

    @pytest.fixture
    def calc(self):
        return ProjectCalculator()

    def test_empty_history_returns_absence_message(self, calc):
        """
        TC-26 | EP: порожня history → рядок 'Історія розрахунків відсутня'.
        """
        # Arrange
        user = User("guest")
        # Act
        report = calc.generate_report(user)
        # Assert
        assert "Історія розрахунків відсутня" in report

    def test_report_contains_username(self, calc):
        """
        TC-27 | Позитивний: звіт містить ім'я користувача.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history({"platforms": ["Webflow"], "complexity": 1,
                              "total_cost": 800.0, "timestamp": "2026-06-03"})
        report = calc.generate_report(user)
        assert "yaroslav" in report

    def test_report_contains_total_cost(self, calc):
        """
        TC-28 | Позитивний: звіт містить відформатовану суму.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history({"platforms": ["Bubble"], "complexity": 2,
                              "total_cost": 1800.0, "timestamp": "2026-06-03"})
        report = calc.generate_report(user)
        assert "1800.00" in report

    def test_report_guest_type_label(self, calc):
        """
        TC-29 | EP: гість → 'Гість' у звіті.
        """
        user = User("guest_user", is_registered=False)
        user.add_to_history({"platforms": ["Make"], "complexity": 1,
                              "total_cost": 500.0, "timestamp": "2026-06-03"})
        report = calc.generate_report(user)
        assert "Гість" in report

    def test_report_registered_type_label(self, calc):
        """
        TC-30 | EP: зареєстрований → 'Зареєстрований' у звіті.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history({"platforms": ["Glide"], "complexity": 3,
                              "total_cost": 1500.0, "timestamp": "2026-06-03"})
        report = calc.generate_report(user)
        assert "Зареєстрований" in report

    def test_report_multiple_records_count(self, calc):
        """
        TC-31 | Позитивний: звіт з двома записами містить '#1' та '#2'.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history({"platforms": ["Webflow"], "complexity": 1,
                              "total_cost": 800.0, "timestamp": "2026-06-03"})
        user.add_to_history({"platforms": ["Bubble"], "complexity": 2,
                              "total_cost": 1800.0, "timestamp": "2026-06-03"})
        report = calc.generate_report(user)
        assert "Розрахунок #1" in report
        assert "Розрахунок #2" in report

    def test_report_complexity_label_low(self, calc):
        """
        TC-32 | EP: complexity=1 → 'Низька' у звіті.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history({"platforms": ["Make"], "complexity": 1,
                              "total_cost": 500.0, "timestamp": "2026-06-03"})
        report = calc.generate_report(user)
        assert "Низька" in report

    def test_report_complexity_label_high(self, calc):
        """
        TC-33 | EP: complexity=3 → 'Висока' у звіті.
        """
        user = User("yaroslav", is_registered=True)
        user.add_to_history({"platforms": ["Glide"], "complexity": 3,
                              "total_cost": 1500.0, "timestamp": "2026-06-03"})
        report = calc.generate_report(user)
        assert "Висока" in report


# ===================================================================
# БЛОК 6 — run_calculation(): інтеграція User + ProjectCalculator
# ===================================================================

class TestRunCalculation:
    """Тести допоміжної функції run_calculation."""

    @pytest.fixture
    def calc(self):
        return ProjectCalculator()

    def test_successful_calculation_adds_to_history(self, calc):
        """
        TC-34 | Позитивний: дозволений розрахунок → запис у history, count=1.
        """
        # Arrange
        user = User("yaroslav", is_registered=True)
        # Act
        run_calculation(user, calc, ["Webflow"], 1)
        # Assert
        assert user.calculation_count == 1
        assert user.calculation_history[0]["total_cost"] == 800.0

    def test_guest_within_limit_calculates(self, calc):
        """
        TC-35 | EP: гість, count=0 < 3 → розрахунок виконується.
        """
        user = User("guest")
        run_calculation(user, calc, ["Make"], 2)
        assert user.calculation_count == 1

    def test_guest_at_limit_blocked(self, calc, capsys):
        """
        TC-36 | BVA: гість, count=3 (ліміт) → розрахунок заблокований,
        history не змінюється, виводиться повідомлення про ліміт.
        """
        # Arrange
        user = User("guest")
        user.calculation_count = 3
        # Act
        run_calculation(user, calc, ["Webflow"], 1)
        # Assert
        assert user.calculation_count == 3          # не збільшився
        assert user.calculation_history == []       # history порожня
        captured = capsys.readouterr()
        assert "Ліміт вичерпано" in captured.out

    def test_calculation_stores_correct_platform_and_complexity(self, calc):
        """
        TC-37 | Позитивний: запис містить правильні платформи та складність.
        """
        user = User("yaroslav", is_registered=True)
        run_calculation(user, calc, ["Bubble", "Glide"], 3)
        rec = user.calculation_history[0]
        assert rec["platforms"] == ["Bubble", "Glide"]
        assert rec["complexity"] == 3
        assert rec["total_cost"] == (1200 + 600) * 2.5

    def test_three_consecutive_guest_calculations(self, calc):
        """
        TC-38 | BVA: гість виконує рівно 3 розрахунки (весь ліміт) → усі проходять.
        """
        user = User("guest")
        run_calculation(user, calc, ["Webflow"], 1)
        run_calculation(user, calc, ["Make"], 1)
        run_calculation(user, calc, ["Glide"], 1)
        assert user.calculation_count == 3

    def test_fourth_guest_calculation_blocked(self, calc):
        """
        TC-39 | BVA: четвертий розрахунок гостя → заблокований, count залишається 3.
        """
        user = User("guest")
        run_calculation(user, calc, ["Webflow"], 1)
        run_calculation(user, calc, ["Make"], 1)
        run_calculation(user, calc, ["Glide"], 1)
        run_calculation(user, calc, ["Bubble"], 2)  # 4-й — заблокований
        assert user.calculation_count == 3
