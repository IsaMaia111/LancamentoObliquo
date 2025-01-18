import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Supondo que estas sejam as coordenadas fornecidas (adicione as suas aqui):
coordenadas_x = np.array([139, 137, 145, 146, 148, 146, 143, 148, 150, 145, 141, 148, 168, 182, 234, 239, 236, 234, 236, 240, 247, 248, 250, 250, 251, 250, 250, 251, 251, 251, 250, 250, 251, 251, 251, 250, 250, 250, 250, 250, 250, 249, 249, 249, 249, 250, 250, 249, 250, 249, 251, 248, 251, 252, 251, 251, 256, 255, 255, 251, 253, 253, 255, 255, 256, 253, 251, 251, 250, 251, 251, 250, 251, 251, 254, 253, 253, 254, 253, 252, 252, 252, 253, 253, 253, 254, 254, 254, 254, 254, 253, 253, 253, 254, 255, 254, 254, 254, 249, 249, 250, 250, 250, 249, 250, 250, 249, 251, 251, 251, 252, 251, 249, 250, 249, 250, 250, 251, 251, 250, 251, 251, 250, 250, 250, 251, 249, 247, 245, 239, 234, 227, 230, 237, 230, 225, 225, 230, 235, 229, 229, 231, 233, 233, 239, 240, 235, 232, 227, 224, 209, 201, 203, 203, 202, 200, 202, 201, 196, 195, 197, 198, 199, 201, 204, 203, 203, 203, 205, 211, 212, 212, 210, 209, 209, 208, 208, 208, 208, 205, 202, 222, 224, 226, 227, 225, 224, 226, 226, 225, 224, 224, 224, 230, 228, 228, 227, 227, 228, 229, 228, 223, 227, 223, 225, 226, 226, 226, 223, 236, 234, 238, 245, 248, 248, 253, 256, 238, 236, 232, 224, 217, 213, 209, 206, 205, 205, 205, 206, 205, 205, 204, 205, 205, 205, 205, 204, 204, 206, 208, 208])  # Distâncias horizontais (em metros, por exemplo)
coordenadas_y = np.array([122, 124, 117, 114, 109, 108, 109, 115, 117, 121, 118, 120, 116, 112, 97, 96, 99, 99, 95, 96, 99, 100, 102, 100, 101, 97, 99, 98, 95, 95, 95, 96, 98, 97, 97, 97, 96, 95, 96, 96, 97, 98, 97, 97, 97, 94, 92, 93, 93, 91, 101, 95, 90, 93, 86, 84, 83, 85, 82, 91, 91, 94, 89, 89, 88, 91, 92, 91, 95, 97, 100, 103, 101, 101, 98, 98, 98, 98, 97, 98, 98, 98, 98, 98, 98, 99, 101, 101, 100, 100, 102, 99, 100, 102, 101, 100, 98, 97, 90, 89, 93, 89, 95, 95, 93, 93, 93, 92, 91, 88, 91, 93, 89, 89, 89, 89, 89, 90, 90, 90, 87, 88, 88, 87, 88, 88, 86, 84, 87, 87, 87, 84, 86, 86, 86, 90, 90, 88, 93, 93, 99, 99, 97, 93, 91, 90, 91, 91, 89, 84, 85, 84, 84, 83, 81, 80, 82, 80, 81, 81, 83, 87, 85, 83, 83, 83, 82, 82, 83, 82, 80, 81, 80, 81, 81, 84, 84, 83, 83, 86, 85, 85, 85, 85, 85, 85, 85, 85, 85, 84, 85, 87, 87, 88, 88, 87, 88, 89, 89, 85, 87, 85, 87, 85, 85, 86, 84, 86, 86, 86, 85, 87, 91, 92, 93, 94, 92, 86, 83, 81, 80, 78, 76, 74, 75, 75, 76, 76, 76, 76, 78, 79, 79, 80, 80, 80, 80, 80, 79])  # Alturas correspondentes

# Função para ajustar os dados a uma parábola: y(x) = ax^2 + bx + c
def parabola(x, a, b, c):
    return a * x**2 + b * x + c

# Ajustar a curva (encontrar os parâmetros a, b, c)
parametros, _ = curve_fit(parabola, coordenadas_x, coordenadas_y)

# Parâmetros da trajetória
a, b, c = parametros
print(f"Parâmetros ajustados: a = {a:.4f}, b = {b:.4f}, c = {c:.4f}")

# Determinar a velocidade inicial e a aceleração
g = -2 * a  # A aceleração (assumindo que a direção y segue a gravidade)
v0 = b      # A velocidade inicial no eixo x (assumindo lançamento horizontal)

print(f"Aceleração (g): {g:.4f} m/s²")
print(f"Velocidade inicial (v0): {v0:.4f} m/s")

# Calcular a distância percorrida (máxima posição x antes que y volte a 0)
distancia_total = (-b + np.sqrt(b**2 - 4*a*c)) / (2*a)  # Fórmula de Bhaskara
print(f"Distância total percorrida: {distancia_total:.4f} m")

# Plotar o gráfico da trajetória
x_fit = np.linspace(min(coordenadas_x), max(coordenadas_x), 500)
y_fit = parabola(x_fit, a, b, c)

plt.figure(figsize=(10, 6))
plt.scatter(coordenadas_x, coordenadas_y, color="red", label="Dados experimentais")
plt.plot(x_fit, y_fit, color="blue", label="Ajuste parabólico")
plt.title("Trajetória do Lançamento Oblíquo")
plt.xlabel("Distância Horizontal (m)")
plt.ylabel("Altura Vertical (m)")
plt.legend()
plt.grid()
plt.show()