import matplotlib.pyplot as plt
import numpy as np

# Dados fornecidos
g = 0.4643  # aceleração em m/s²
v0 = 1.9036  # velocidade inicial em m/s
theta = 45  # ângulo de lançamento em graus
d = 0.0339  # distância total percorrida em metros

# Convertendo o ângulo para radianos
theta_rad = np.radians(theta)

# Calculando o tempo total de voo
t_total = d / (v0 * np.cos(theta_rad))

# Gerando os pontos de tempo
t = np.linspace(0, t_total, num=500)

# Calculando as coordenadas x e y
x = v0 * np.cos(theta_rad) * t
y = v0 * np.sin(theta_rad) * t - 0.5 * g * t**2

# Plotando o gráfico
plt.plot(x, y)
plt.title('Trajetória do Lançamento Oblíquo')
plt.xlabel('Distância (m)')
plt.ylabel('Altura (m)')
plt.grid(True)
plt.show()