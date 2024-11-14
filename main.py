import streamlit as st
import random
import matplotlib.pyplot as plt


# Ввод количество пользователей и комиссии
payout_min_multiplier = st.number_input("Минимальный коэффициент:", min_value=1.5, value=1.5, step=0.1)
payout_max_multiplier = st.number_input("Максимальный коэффициент:", min_value=1.6, value=2.0, step=0.1)
initial_deposit = st.number_input("Вклад:", min_value=1, value=5)
num_users = st.number_input("Количество пользователей:", min_value=1, value=1)
commission = st.number_input("Комиссия (%):", min_value=0, max_value=100, value=20)
use_str = st.checkbox("Показывать строки пользователей:", value=False)

# Расчет вкладов и переменных
bank_sum = num_users * initial_deposit
commission_amount = (commission / 100) * bank_sum
in_bank = bank_sum - commission_amount
payout = 0.0

# Генерация случайных коэффициентов выплат для каждого пользователя
payout_multipliers = [round(random.uniform(payout_min_multiplier, payout_max_multiplier), 1) for _ in range(num_users)]

# Статистика выплат
received_payout_count = 0
not_received_payout_count = num_users

# Расчет автоматических выплат
for i in range(num_users):
    payout_amount = initial_deposit * payout_multipliers[i]

    if in_bank >= payout_amount:
        in_bank -= payout_amount  # Вычитаем из in_bank
        payout += payout_amount   # Записываем в payout
        received_payout_count += 1
        not_received_payout_count -= 1
        if use_str:
            st.success(f"Пользователю {i+1} выплачено: {payout_amount:.2f} TON (коэффициент: {payout_multipliers[i]})")
    else:
        if use_str:
            st.error(f"Недостаточно средств в банке для выплаты пользователю {i + 1}")

# Подготовка данных для графика
labels = ['Получили выплату', 'Не получили выплату']
sizes = [received_payout_count, not_received_payout_count]
colors = ['#4CAF50', '#FF5733']

# Построение графика
fig, ax = plt.subplots()
ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
ax.axis('equal')  # Равные оси для правильного отображения круга

# Отображение графика
st.pyplot(fig)

# Вывод информации
st.write(f"Сумма всех вкладов (bank_sum): {bank_sum:.2f} TON")
st.write(f"Сумма комиссии (commission_amount): {commission_amount:.2f} TON")
st.write(f"Сумма всех выплат (payout): {payout:.2f} TON")
st.write(f"Сумма в банке (in_bank): {in_bank:.2f} TON")