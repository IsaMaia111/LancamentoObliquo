import cv2
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def calibrate_scale_with_mouse(frame):
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

    while True:
        cv2.imshow("Calibração", frame_copy)
        key = cv2.waitKey(1) & 0xFF
        if key == 13 and len(ref_points) == 2: 
            break

    cv2.destroyAllWindows()

    if len(ref_points) == 2:
        pixel_distance = np.linalg.norm(np.array(ref_points[0]) - np.array(ref_points[1]))
        real_distance = 1.5
        scale_factor = real_distance / pixel_distance
        print(f"Distância em pixels: {pixel_distance:.2f} pixels")
        print(f"Distância real: {real_distance:.2f} metros")
        return scale_factor
    print("Calibração falhou. Tente novamente.")
    return None

def track_moving_object(video_path):
    def update_frame():
        nonlocal prev_gray, total_distance, total_velocity, total_acceleration, object_positions, frame_tk, object_height_meters
        nonlocal max_height, max_velocity, max_distance, max_acceleration
        nonlocal x_traj, y_traj

        ret, frame = cap.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        frame_diff = cv2.absdiff(prev_gray, gray)
        _, thresh = cv2.threshold(frame_diff, 10, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        largest_contour = None
        max_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 20 and area > max_area: 
                max_area = area
                largest_contour = contour

        if largest_contour is not None:
            (x, y, w, h) = cv2.boundingRect(largest_contour)
            center_x, center_y = x + w // 2, y + h // 2

            if object_positions:
                prev_x, prev_y = object_positions[-1]
                distance = np.linalg.norm([center_x - prev_x, center_y - prev_y])
                total_distance += distance
                max_distance = max(max_distance, total_distance)

                velocity = distance / frame_time
                velocities.append(velocity)
                total_velocity += velocity
                max_velocity = max(max_velocity, velocity)

                if len(velocities) > 1:
                    acceleration = (velocities[-1] - velocities[-2]) / frame_time
                    accelerations.append(acceleration)
                    total_acceleration += abs(acceleration)
                    max_acceleration = max(max_acceleration, abs(acceleration))

            object_positions.append((center_x, center_y))

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            object_height_pixels = frame.shape[0] - center_y
            object_height_meters = object_height_pixels * pixel_to_meter
            max_height = max(max_height, object_height_meters)

            x_traj.append(total_distance * pixel_to_meter)
            y_traj.append(object_height_meters)

        prev_gray = gray

        total_distance_m = total_distance * pixel_to_meter
        total_velocity_mps = (total_velocity / len(velocities)) * pixel_to_meter if velocities else 0
        total_acceleration_mps2 = (total_acceleration / len(accelerations)) * pixel_to_meter if accelerations else 0

        info_text.set(f"Distância: {total_distance_m:.2f} m\n"
                      f"Velocidade: {total_velocity_mps:.2f} m/s\n"
                      f"Aceleração: {total_acceleration_mps2:.2f} m/s²\n"
                      f"Altura: {object_height_meters:.2f} m\n")

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame_rgb)
        frame_tk = ImageTk.PhotoImage(image=frame_pil)
        video_label.imgtk = frame_tk
        video_label.configure(image=frame_tk)

        if len(x_traj) > 1:
            ax.clear()
            ax.plot(x_traj, y_traj, label="Trajetória", color="blue")
            ax.set_title("Gráfico de Trajetória")
            ax.set_xlabel("Distância (m)")
            ax.set_ylabel("Altura (m)")
            ax.set_ylim(0, max(y_traj) + 1)
            ax.grid()
            ax.legend()
            canvas.draw()

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
    object_height_meters = 0
    max_height = 0
    max_velocity = 0
    max_distance = 0
    max_acceleration = 0

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_time = 1 / fps
    velocities = []
    accelerations = []
    stop_flag = False
    frame_tk = None
    x_traj = []
    y_traj = []

    root = tk.Tk()
    root.title("Dashboard de Rastreamento de Objetos em Movimento")
    root.geometry("1200x800")
    root.configure(bg="#121212")

    # Card para o vídeo
    video_card = tk.Frame(root, bg="#1e1e1e", relief="raised", bd=2)
    video_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
    video_label = tk.Label(video_card, bg="#1e1e1e")
    video_label.pack(fill="both", expand=True)

    # Card para o gráfico
    graph_card = tk.Frame(root, bg="#1e1e1e", relief="raised", bd=2)
    graph_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
    figure = plt.Figure(figsize=(6, 4), dpi=100)
    ax = figure.add_subplot(111)
    canvas = FigureCanvasTkAgg(figure, graph_card)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # Card para informações
    info_card = tk.Frame(root, bg="#1e1e1e", relief="raised", bd=2)
    info_card.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
    info_text = tk.StringVar()
    info_label = tk.Label(info_card, textvariable=info_text, bg="#1e1e1e", fg="white", font=("Arial", 12), justify="left", wraplength=300)
    info_label.pack(fill="both", expand=True, padx=10, pady=10)

    # Botão de fechar
    close_button = tk.Button(root, text="Fechar", command=on_close, font=("Arial", 12), bg="#e74c3c", fg="white", relief="raised", bd=2)
    close_button.grid(row=2, column=0, columnspan=2, pady=10, sticky="e")

    # Ajustando a estrutura da grade
    root.grid_rowconfigure(0, weight=3)
    root.grid_rowconfigure(1, weight=2)
    root.grid_rowconfigure(2, weight=0)
    root.grid_columnconfigure(0, weight=3)
    root.grid_columnconfigure(1, weight=1)

    # Inicia a atualização do frame
    update_frame()
    root.mainloop()

# Caminho do vídeo
video_path = "video.mp4"

# Rastreamento do objeto em movimento
track_moving_object(video_path)

