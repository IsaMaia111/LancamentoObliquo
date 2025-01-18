import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def calibrate_scale_with_mouse(frame):
    """
    Permite ao usuário selecionar com o mouse a distância entre dois pontos no frame.
    Retorna a escala em metros por pixel com base na distância fixa de 1,5 metros.
    """
    def draw_line(event, x, y, flags, param):
        nonlocal ref_points, drawing
        if event == cv2.EVENT_LBUTTONDOWN:
            ref_points = [(x, y)]
            drawing = True
        elif event == cv2.EVENT_LBUTTONUP and drawing:
            ref_points.append((x, y))
            drawing = False
            cv2.line(frame_copy, ref_points[0], ref_points[1], (0, 255, 0), 2)
            cv2.imshow("Calibração", frame_copy)

    ref_points = []
    drawing = False
    frame_copy = frame.copy()

    cv2.imshow("Calibração", frame_copy)
    cv2.setMouseCallback("Calibração", draw_line)

    # Aguarda o usuário finalizar a calibração
    while True:
        cv2.imshow("Calibração", frame_copy)
        key = cv2.waitKey(1) & 0xFF
        if key == 13 and len(ref_points) == 2:  # ENTER para finalizar
            break

    cv2.destroyAllWindows()

    if len(ref_points) == 2:
        pixel_distance = np.linalg.norm(np.array(ref_points[0]) - np.array(ref_points[1]))
        real_distance = 1.5  # Define 1,5 metro como distância fixa
        scale_factor = real_distance / pixel_distance
        print(f"Distância em pixels: {pixel_distance:.2f} pixels")
        print(f"Distância real: {real_distance:.2f} metros")
        return scale_factor
    print("Calibração falhou. Tente novamente.")
    return None

def calculate_trajectory(velocity):
    """
    Calcula os pontos da trajetória de um lançamento oblíquo com ângulo de 45 graus.
    Retorna os vetores X e Y para o gráfico em formato de parábola invertida.
    """
    g = 9.8  # Gravidade em m/s²
    angle = np.radians(45)  # Ângulo em radianos
    t_total = (2 * velocity * np.sin(angle)) / g  # Tempo total do voo
    t = np.linspace(0, t_total, num=500)  # Vetor de tempo

    x = velocity * np.cos(angle) * t
    y = velocity * np.sin(angle) * t - 0.5 * g * t**2
    return x, y

def track_moving_object(video_path):
    def update_frame():
        nonlocal prev_gray, total_distance, total_velocity, total_acceleration, object_positions, frame_tk

        ret, frame = cap.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calcula a diferença entre o frame atual e o anterior
        frame_diff = cv2.absdiff(prev_gray, gray)
        _, thresh = cv2.threshold(frame_diff, 10, 255, cv2.THRESH_BINARY)

        # Aplica operações morfológicas para limpar ruídos
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # Encontra contornos no frame de diferença
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        largest_contour = None
        max_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 20 and area > max_area:  # Filtra movimentos menores para capturar detalhes
                max_area = area
                largest_contour = contour

        if largest_contour is not None:
            (x, y, w, h) = cv2.boundingRect(largest_contour)
            center_x, center_y = x + w // 2, y + h // 2

            if object_positions:
                prev_x, prev_y = object_positions[-1]
                distance = np.linalg.norm([center_x - prev_x, center_y - prev_y])
                total_distance += distance

                velocity = distance / frame_time
                velocities.append(velocity)
                total_velocity += velocity

                if len(velocities) > 1:
                    acceleration = (velocities[-1] - velocities[-2]) / frame_time
                    accelerations.append(acceleration)
                    total_acceleration += abs(acceleration)

            object_positions.append((center_x, center_y))

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

        prev_gray = gray

        # Conversões para métricas reais
        total_distance_m = total_distance * pixel_to_meter
        total_velocity_mps = (total_velocity / len(velocities)) * pixel_to_meter if velocities else 0
        total_acceleration_mps2 = (total_acceleration / len(accelerations)) * pixel_to_meter if accelerations else 0

        # Atualiza o gráfico com o lançamento oblíquo
        if velocities:  # Garante que temos dados suficientes para plotar
            x_traj, y_traj = calculate_trajectory(total_velocity_mps)
            ax.clear()
            ax.plot(x_traj, y_traj, label="Trajetória (Parábola Invertida)", color="blue")
            ax.set_title("Lançamento Oblíquo - Trajetória Parabólica", fontsize=14)
            ax.set_xlabel("Distância Horizontal (m)", fontsize=12)
            ax.set_ylabel("Altura (m)", fontsize=12)
            ax.grid(True, linestyle='--', alpha=0.7)

            # Ajusta os limites do gráfico
            ax.set_xlim(0, max(x_traj))
            ax.set_ylim(0, max(y_traj) + 1)
            canvas.draw()

        # Atualiza o texto das informações
        info_text.set(f"Distância: {total_distance_m:.2f} m\n"
                      f"Velocidade: {total_velocity_mps:.2f} m/s\n"
                      f"Aceleração: {total_acceleration_mps2:.2f} m/s²")

        # Exibe o vídeo no rótulo
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_tk = ImageTk.PhotoImage(image=frame_pil)
        video_label.imgtk = frame_tk
        video_label.configure(image=frame_tk)

        if not stop_flag:
            root.after(10, update_frame)

    def on_close():
        nonlocal stop_flag
        stop_flag = True
        cap.release()
        root.destroy()

    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    if not ret:
        print("Erro ao carregar o vídeo.")
        return

    pixel_to_meter = calibrate_scale_with_mouse(frame)
    if pixel_to_meter is None:
        print("Calibração falhou. Encerrando.")
        return

    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    object_positions = []
    total_distance = 0
    total_velocity = 0
    total_acceleration = 0

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_time = 1 / fps
    velocities = []
    accelerations = []
    stop_flag = False
    frame_tk = None  # Adiciona a variável frame_tk para manter a referência

    # Configurações da janela
    root = tk.Tk()
    root.title("Dashboard de Rastreamento de Objetos em Movimento")
    root.configure(bg="#000000")  # Preto fosco
    root.attributes('-fullscreen', True)  # Tela cheia

    # Configuração da grade com 4 áreas
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)

    # Card para o vídeo
    video_label = tk.Label(root, bg="#1c1c1c")
    video_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Card para o gráfico
    figure = plt.Figure(figsize=(5, 4), dpi=100)
    ax = figure.add_subplot(111)
    ax.set_facecolor("#000000")
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    canvas = FigureCanvasTkAgg(figure, root)
    canvas.get_tk_widget().grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Card para dados finais
    info_text = tk.StringVar()
    info_label = tk.Label(root, textvariable=info_text, bg="#1c1c1c", fg="white", font=("Arial", 12), justify="left")
    info_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Card para botão de fechar
    close_button = tk.Button(root, text="Fechar", command=on_close, font=("Arial", 14), bg="#e74c3c", fg="white")
    close_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    # Atualiza o frame
    update_frame()
    root.mainloop()

# Caminho do vídeo
video_path = "video.mp4"

# Rastreamento do objeto em movimento
track_moving_object(video_path)
