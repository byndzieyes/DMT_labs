import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Порядковий номер варіанта за журналом
N = 7

output_dir = "plots"
os.makedirs(output_dir, exist_ok=True)

# -------------------------------------------------------------
# a. Розподіл Бернуллі: p = 1 / (N + 1)
# -------------------------------------------------------------
p_bern = 1 / (N + 1)
x_bern = np.array([0, 1])
y_bern = stats.bernoulli.pmf(x_bern, p_bern)

plt.figure(figsize=(7, 5))
plt.bar(x_bern, y_bern, color='royalblue', width=0.3, edgecolor='black')
plt.xticks([0, 1])
plt.ylim(0, 1)
plt.title(f"a. Розподіл Бернуллі (p = {p_bern:.3f})")
plt.xlabel("Значення (x)")
plt.ylabel("P(X = x)")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "a_bernoulli.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# b. Біноміальний розподіл: p = 1 / (N + 1), n = N + 2
# -------------------------------------------------------------
p_binom = 1 / (N + 1)
n_binom = N + 2
x_binom = np.arange(0, n_binom + 1)
y_binom = stats.binom.pmf(x_binom, n_binom, p_binom)

plt.figure(figsize=(7, 5))
plt.stem(x_binom, y_binom, basefmt=" ")
plt.xticks(x_binom)
plt.title(f"b. Біноміальний розподіл (n = {n_binom}, p = {p_binom:.3f})")
plt.xlabel("Кількість успіхів (x)")
plt.ylabel("P(X = x)")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "b_binomial.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# c. Розподіл Пуассона: lambda = N + 10, k_max = N + 5
# -------------------------------------------------------------
lambda_poiss = N + 10
k_max = N + 5
x_poiss = np.arange(0, k_max + 1)
y_poiss = stats.poisson.pmf(x_poiss, lambda_poiss)

plt.figure(figsize=(7, 5))
plt.stem(x_poiss, y_poiss, basefmt=" ", linefmt='green', markerfmt='go')
plt.xticks(x_poiss)
plt.title(f"c. Розподіл Пуассона (λ = {lambda_poiss}, k_max = {k_max})")
plt.xlabel("Кількість подій (k)")
plt.ylabel("P(X = k)")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "c_poisson.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# d. Рівномірний розподіл: a = -N, b = N
# -------------------------------------------------------------
a_unif = -N
b_unif = N
x_unif = np.linspace(a_unif - 2, b_unif + 2, 500)
y_unif = stats.uniform.pdf(x_unif, loc=a_unif, scale=(b_unif - a_unif))

plt.figure(figsize=(7, 5))
plt.plot(x_unif, y_unif, color='darkorange', linewidth=2)
plt.fill_between(x_unif, y_unif, color='orange', alpha=0.2)
plt.title(f"d. Рівномірний розподіл (a = {a_unif}, b = {b_unif})")
plt.xlabel("x")
plt.ylabel("Густина ймовірності f(x)")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "d_uniform.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# e. Нормальний розподіл: a = N, sigma^2 = N / 2
# -------------------------------------------------------------
mu_norm = N
sigma2_norm = N / 2
sigma_norm = np.sqrt(sigma2_norm)
x_norm = np.linspace(mu_norm - 4 * sigma_norm, mu_norm + 4 * sigma_norm, 500)
y_norm = stats.norm.pdf(x_norm, loc=mu_norm, scale=sigma_norm)

plt.figure(figsize=(7, 5))
plt.plot(x_norm, y_norm, color='crimson', linewidth=2)
plt.fill_between(x_norm, y_norm, color='crimson', alpha=0.2)
plt.title(f"e. Нормальний розподіл (a = {mu_norm}, σ² = {sigma2_norm})")
plt.xlabel("x")
plt.ylabel("Густина f(x)")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "e_normal.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# f. Розподіл Парето: alpha = x0 = N
# -------------------------------------------------------------
alpha_pareto = N
x0_pareto = N
x_pareto = np.linspace(x0_pareto, x0_pareto * 2.5, 500)
y_pareto = stats.pareto.pdf(x_pareto, b=alpha_pareto, scale=x0_pareto)

plt.figure(figsize=(7, 5))
plt.plot(x_pareto, y_pareto, color='purple', linewidth=2)
plt.fill_between(x_pareto, y_pareto, color='purple', alpha=0.2)
plt.title(f"f. Розподіл Парето (α = {alpha_pareto}, x₀ = {x0_pareto})")
plt.xlabel("x")
plt.ylabel("Густина f(x)")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "f_pareto.png"), dpi=300)
plt.close()

# -------------------------------------------------------------
# g. Розподіл Стьюдента: alpha = N (ступені вільності)
# -------------------------------------------------------------
df_student = N
x_t = np.linspace(-4, 4, 500)
y_t = stats.t.pdf(x_t, df=df_student)

plt.figure(figsize=(7, 5))
plt.plot(x_t, y_t, color='teal', linewidth=2)
plt.fill_between(x_t, y_t, color='teal', alpha=0.2)
plt.title(f"g. Розподіл Стьюдента (df = {df_student})")
plt.xlabel("x")
plt.ylabel("Густина f(x)")
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "g_student.png"), dpi=300)
plt.close()

print(f"Усі 7 графіків успішно збережено в папку '{output_dir}/'")