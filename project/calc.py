"""
Модуль: Калькулятор витрат на no-code проєкти
Автор: Могила Ярослав Романович, група ПЗПІ-25-4
Дисципліна: Основи програмної інженерії
"""

from datetime import datetime


class User:
    """
    Клас, що представляє користувача системи.

    Ролі:
    - Гість (is_registered=False): ліміт GUEST_LIMIT розрахунків.
    - Зареєстрований (is_registered=True): без ліміту, зберігається історія.
    """

    GUEST_LIMIT = 3

    def __init__(self, username: str, is_registered: bool = False):
        """
        :param username: ім'я користувача (str).
        :param is_registered: True — зареєстрований, False — гість.
        """
        if not username or not isinstance(username, str):
            raise ValueError("username має бути непорожнім рядком.")
        self.username: str = username
        self.is_registered: bool = is_registered
        self.calculation_history: list = []
        self.calculation_count: int = 0

    def can_calculate(self) -> bool:
        """
        Повертає True, якщо користувач має право виконати розрахунок.
        Зареєстрований — завжди True.
        Гість — True, якщо calculation_count < GUEST_LIMIT.
        """
        if self.is_registered:
            return True
        return self.calculation_count < self.GUEST_LIMIT

    def add_to_history(self, record: dict) -> None:
        """
        Зберігає запис розрахунку в history та збільшує лічильник.

        :param record: dict із ключами platforms, complexity, total_cost, timestamp.
        """
        self.calculation_history.append(record)
        self.calculation_count += 1


class ProjectCalculator:
    """
    Калькулятор вартості розробки no-code проєктів.

    Підтримує платформи: Webflow, Bubble, Glide, Make.
    Складність: 1 (низька), 2 (середня), 3 (висока).
    """

    COMPLEXITY_FACTORS = {
        1: 1.0,
        2: 1.5,
        3: 2.5,
    }

    def __init__(self):
        """Ініціалізує базові тарифи платформ (USD)."""
        self.platform_rates: dict = {
            "Webflow": 800,
            "Bubble":  1200,
            "Glide":   600,
            "Make":    500,
        }

    def calculate_cost(self, platforms_list: list, complexity: int) -> float:
        """
        Розраховує вартість проєкту.

        Алгоритм: сума тарифів обраних платформ × коефіцієнт складності.

        :param platforms_list: список платформ, наприклад ["Webflow", "Bubble"].
        :param complexity: рівень складності 1..3.
        :return: загальна вартість (float).
        :raises ValueError: якщо platforms_list порожній, complexity від'ємний,
                            complexity поза діапазоном або платформа невідома.
        """
        if not platforms_list:
            raise ValueError("Список платформ не може бути порожнім.")

        if complexity < 0:
            raise ValueError("Складність не може бути від'ємною.")

        if complexity not in self.COMPLEXITY_FACTORS:
            raise ValueError(
                f"Складність має бути від 1 до 3, отримано: {complexity}."
            )

        base_cost = 0.0
        for platform in platforms_list:
            if platform not in self.platform_rates:
                raise ValueError(
                    f"Невідома платформа: '{platform}'. "
                    f"Доступні: {list(self.platform_rates.keys())}."
                )
            base_cost += self.platform_rates[platform]

        return base_cost * self.COMPLEXITY_FACTORS[complexity]

    def generate_report(self, user: User) -> str:
        """
        Генерує текстовий звіт на основі history користувача.

        :param user: об'єкт User.
        :return: форматований рядок звіту.
        """
        if not user.calculation_history:
            return (
                f"Звіт для користувача '{user.username}':\n"
                "Історія розрахунків відсутня."
            )

        complexity_labels = {1: "Низька", 2: "Середня", 3: "Висока"}
        lines = [
            "=" * 50,
            "  ЗВІТ: Калькулятор витрат на no-code проєкти",
            f"  Користувач : {user.username}",
            f"  Тип        : {'Зареєстрований' if user.is_registered else 'Гість'}",
            f"  Розрахунків: {user.calculation_count}",
            "=" * 50,
        ]
        for idx, rec in enumerate(user.calculation_history, start=1):
            c = rec.get("complexity", "-")
            lines += [
                f"\n  Розрахунок #{idx}",
                f"  Платформи  : {', '.join(rec.get('platforms', []))}",
                f"  Складність : {complexity_labels.get(c, str(c))} ({c})",
                f"  Вартість   : ${rec.get('total_cost', 0):.2f}",
                f"  Дата       : {rec.get('timestamp', '—')}",
            ]
        lines.append("\n" + "=" * 50)
        return "\n".join(lines)


def run_calculation(
    user: User,
    calculator: ProjectCalculator,
    platforms_list: list,
    complexity: int,
) -> None:
    """
    Виконує розрахунок від імені користувача з перевіркою ліміту.

    :param user: об'єкт User.
    :param calculator: об'єкт ProjectCalculator.
    :param platforms_list: список платформ.
    :param complexity: рівень складності 1..3.
    """
    if not user.can_calculate():
        print(
            f"[!] Ліміт вичерпано для гостя '{user.username}'. "
            "Зареєструйтесь для необмеженого доступу."
        )
        return

    cost = calculator.calculate_cost(platforms_list, complexity)
    record = {
        "platforms": platforms_list,
        "complexity": complexity,
        "total_cost": cost,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    user.add_to_history(record)
    print(
        f"[✓] {', '.join(platforms_list)} | складність {complexity} | "
        f"вартість: ${cost:.2f}"
    )


if __name__ == "__main__":
    calc = ProjectCalculator()

    print("=== Гість (ліміт 3) ===")
    guest = User("guest_user")
    for pl, cx in [
        (["Webflow"], 1),
        (["Bubble", "Make"], 2),
        (["Glide"], 3),
        (["Webflow", "Bubble"], 1),  # 4-та — заблокована
    ]:
        run_calculation(guest, calc, pl, cx)
    print(calc.generate_report(guest))

    print("\n=== Зареєстрований ===")
    reg = User("yaroslav_mohyla", is_registered=True)
    run_calculation(reg, calc, ["Webflow", "Bubble", "Glide"], 3)
    run_calculation(reg, calc, ["Make"], 1)
    print(calc.generate_report(reg))
