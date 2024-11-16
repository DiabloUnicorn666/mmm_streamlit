import streamlit as st
import random
import matplotlib.pyplot as plt
import statistics
import pandas as pd
import numpy as np


st.sidebar.title("Параметры")

# st.set_page_config(layout="wide")

# Ввод количество пользователей и комиссии
seed = st.sidebar.number_input("Seed:", min_value=0, value=42)
mean_followers = st.sidebar.number_input("Среднее количество подписчиков:", min_value=1, value=30)
sigma_followers = st.sidebar.number_input("Стандартное отклонение количества подписчиков:", min_value=1, value=15)
payout_min_multiplier = st.sidebar.number_input("Минимальный коэффициент:", min_value=0.0, value=1.3, step=0.01)
payout_max_multiplier = st.sidebar.number_input("Максимальный коэффициент:", min_value=0.0, value=2.0, step=0.01)
initial_deposit = st.sidebar.number_input("Вклад:", min_value=1, value=5)
num_users = st.sidebar.number_input("Количество пользователей:", min_value=1, value=10000)
max_followers = st.sidebar.number_input("Максимальное количество подписчиков:", min_value=1, value=100)
commission = st.sidebar.number_input("Комиссия (%):", min_value=0, max_value=100, value=20)
first_parent = st.sidebar.number_input("(%) Вознаграждение Родитель первого уровня:", min_value=0.0, value=1.0, step=0.1)
second_parent = st.sidebar.number_input("(%) Вознаграждение Родитель второго уровня:", min_value=0.0, value=0.5, step=0.1)
show_zero_payout = st.sidebar.checkbox("Показывать выплаты равные 0:", value=False)

use_random_payout_multiplier = st.sidebar.checkbox("Использовать случайный модификатор коэффициента выплат:", value=False)
if use_random_payout_multiplier:
    random_payout_multiplier_sigma = st.sidebar.number_input("Стандартное отклонение модификатора коэффициента выплат:", min_value=0.0, value=0.1, step=0.01)
    random_payout_multiplier_mu = st.sidebar.number_input("Среднее значение модификатора коэффициента выплат:", min_value=0.0, value=0.01, step=0.01)

use_str = st.sidebar.checkbox("Показывать строки пользователей:", value=False)

def set_seed(seed):
    np.random.seed(seed)
    random.seed(seed)


def calculate_payout_multiplier(followers:float):
    # linear function capped by payout_min_multiplier and payout_max_multiplier
    min_followers = 1.0
    scale = min_followers / max_followers
    result = followers* scale
    # st.write(f"followers: {followers}, result: {result}")
    # scale it to payout_min_multiplier and payout_max_multiplier
    result = result * (payout_max_multiplier - payout_min_multiplier) + payout_min_multiplier
    if use_random_payout_multiplier:
        result = result + random.normalvariate(mu=random_payout_multiplier_mu, sigma=random_payout_multiplier_sigma)
    return result


set_seed(seed)

# Расчет вкладов и переменных
bank_sum = num_users * initial_deposit
commission_amount = (commission / 100) * bank_sum
first_parent_amount = (first_parent / 100) * bank_sum
second_parent_amount = (second_parent / 100) * bank_sum
in_bank = bank_sum - commission_amount - second_parent_amount - first_parent_amount
payout = 0.0

followers = [min(100, max(1, round(random.normalvariate(mu=mean_followers, sigma=sigma_followers), 0))) for _ in range(num_users)]
df = pd.DataFrame(followers, columns=['Количество подписчиков'])
st.pyplot(df.plot.hist(bins=10, edgecolor='black').figure)

# # Генерация случайных коэффициентов выплат для каждого пользователя
# # payout_multipliers = [round(random.uniform(payout_min_multiplier, payout_max_multiplier), 1) for _ in range(num_users)]
# payout_multipliers = [round(random.normalvariate(
#             mu=statistics.mean([payout_min_multiplier, payout_max_multiplier]),
#             sigma=0.1),
#         2) for _ in range(num_users)]

if use_random_payout_multiplier:
    random_payout_multiplier_varoations = [random.normalvariate(mu=random_payout_multiplier_mu, sigma=random_payout_multiplier_sigma) for _ in range(num_users)]
    df = pd.DataFrame(random_payout_multiplier_varoations, columns=['Модификатор коэффициента выплат'])
    st.pyplot(df.plot.hist(bins=10, edgecolor='black').figure)

payout_multipliers = [calculate_payout_multiplier(followers[i]) for i in range(num_users)]
df = pd.DataFrame(payout_multipliers, columns=['Коэффициент выплат'])

st.pyplot(df.plot.hist(bins=10, edgecolor='black').figure)

# Статистика выплат
received_payout_count = 0
not_received_payout_count = num_users
payout_amounts = []

# Расчет автоматических выплат
for i in range(num_users):
    payout_amount = initial_deposit * payout_multipliers[i]

    if in_bank >= payout_amount:
        in_bank -= payout_amount  # Вычитаем из in_bank
        payout += payout_amount   # Записываем в payout
        received_payout_count += 1
        not_received_payout_count -= 1
        payout_amounts.append(payout_amount)
        if use_str:
            st.success(f"Пользователю {i+1} выплачено: {payout_amount:.2f} TON (коэффициент: {payout_multipliers[i]})")
    else:
        payout_amounts.append(0)
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

df = pd.DataFrame(payout_amounts, columns=['Сумма выплаты'])
if not show_zero_payout:
    df = df[df['Сумма выплаты'] > 0]
st.pyplot(df.plot.hist(bins=100, edgecolor='black').figure)


# Вывод информации
st.write(f"Сумма всех вкладов (bank_sum): {bank_sum:.2f} TON")
st.write(f"Сумма комиссии (commission_amount): {commission_amount:.2f} TON")
st.write(f"На вознаграждение первого уровня: {first_parent_amount:.2f} TON")
st.write(f"На вознаграждение второго уровня: {second_parent_amount:.2f} TON")
st.write(f"Сумма всех выплат (payout): {payout:.2f} TON")
st.write(f"Количество пользователей, получивших выплату: {received_payout_count}")
st.write(f"Количество пользователей, не получивших выплату: {not_received_payout_count}")
st.write(f"Сумма в банке (in_bank): {in_bank:.2f} TON")

