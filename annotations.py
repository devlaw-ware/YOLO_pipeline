import cv2
import os

# =========================================
# CONFIGURAÇÕES
# =========================================

IMAGE_DIR = "dataset/images/train"
LABEL_DIR = "dataset/labels/train"

CLASSES = {
    0: "cat",
    1: "dog"
}

# =========================================
# VARIÁVEIS GLOBAIS
# =========================================

drawing = False
ix, iy = -1, -1

current_image = None
clone = None
annotations = []

selected_class = 0

# =========================================
# FUNÇÃO YOLO
# =========================================

def convert_to_yolo(display_size, original_size, box):

    display_w, display_h = display_size
    original_w, original_h = original_size

    scale_x = original_w / display_w
    scale_y = original_h / display_h

    x1 = box[0] * scale_x
    y1 = box[1] * scale_y
    x2 = box[2] * scale_x
    y2 = box[3] * scale_y

    x_center = (x1 + x2) / 2.0
    y_center = (y1 + y2) / 2.0

    width = x2 - x1
    height = y2 - y1

    x_center /= original_w
    width /= original_w

    y_center /= original_h
    height /= original_h

    return (
        round(x_center, 6),
        round(y_center, 6),
        round(width, 6),
        round(height, 6)
    )

# =========================================
# REDESENHAR BOXES
# =========================================

def redraw_image():

    global current_image

    current_image = clone.copy()

    for ann in annotations:

        class_id, x1, y1, x2, y2 = ann

        cv2.rectangle(
            current_image,
            (x1, y1),
            (x2, y2),
            (0, 255, 0),
            2
        )

        cv2.putText(
            current_image,
            CLASSES[class_id],
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

# =========================================
# EVENTO MOUSE
# =========================================

def draw_rectangle(event, x, y, flags, param):

    global ix, iy
    global drawing
    global annotations
    global current_image

    if event == cv2.EVENT_LBUTTONDOWN:

        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:

        if drawing:

            temp_image = current_image.copy()

            cv2.rectangle(
                temp_image,
                (ix, iy),
                (x, y),
                (0, 255, 0),
                2
            )

            cv2.imshow(
                "YOLO Annotation Tool",
                temp_image
            )

    elif event == cv2.EVENT_LBUTTONUP:

        drawing = False

        x1 = min(ix, x)
        y1 = min(iy, y)
        x2 = max(ix, x)
        y2 = max(iy, y)

        annotations.append(
            (
                selected_class,
                x1,
                y1,
                x2,
                y2
            )
        )

        redraw_image()

# =========================================
# PERCORRER SUBPASTAS
# =========================================

for class_folder in ["cats", "dogs"]:

    image_folder = os.path.join(
        IMAGE_DIR,
        class_folder
    )

    label_folder = os.path.join(
        LABEL_DIR,
        class_folder
    )

    os.makedirs(label_folder, exist_ok=True)

    image_files = [
        f for f in os.listdir(image_folder)
        if f.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
    ]

    for image_name in image_files:

        image_path = os.path.join(
            image_folder,
            image_name
        )

        original_image = cv2.imread(image_path)

        if original_image is None:
            continue

        # =========================================
        # REDIMENSIONAMENTO
        # =========================================

        MAX_WIDTH = 1280
        MAX_HEIGHT = 720

        h, w = original_image.shape[:2]

        scale = min(
            MAX_WIDTH / w,
            MAX_HEIGHT / h,
            1
        )

        new_w = int(w * scale)
        new_h = int(h * scale)

        current_image = cv2.resize(
            original_image,
            (new_w, new_h)
        )

        clone = current_image.copy()

        annotations = []

        print(f"\nImagem: {image_name}")
        print(f"Pasta: {class_folder}")

        print("Teclas:")
        print("0 = gato")
        print("1 = cachorro")
        print("S = salvar")
        print("R = resetar")
        print("N = próxima imagem")
        print("ESC = sair")

        cv2.namedWindow(
            "YOLO Annotation Tool",
            cv2.WINDOW_NORMAL
        )

        cv2.setMouseCallback(
            "YOLO Annotation Tool",
            draw_rectangle
        )

        while True:

            display = current_image.copy()

            cv2.putText(
                display,
                f"Classe atual: {CLASSES[selected_class]}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2
            )

            cv2.imshow(
                "YOLO Annotation Tool",
                display
            )

            key = cv2.waitKey(1) & 0xFF

            # =========================================
            # CLASSES
            # =========================================

            if key == ord("0"):
                selected_class = 0

            elif key == ord("1"):
                selected_class = 1

            # =========================================
            # RESET
            # =========================================

            elif key == ord("r"):

                annotations = []

                current_image = cv2.resize(
                    original_image,
                    (new_w, new_h)
                )

                clone = current_image.copy()

                print("Annotations resetadas")

            # =========================================
            # SALVAR
            # =========================================

            elif key == ord("s"):

                display_h, display_w = current_image.shape[:2]

                original_h, original_w = original_image.shape[:2]

                label_path = os.path.join(
                    label_folder,
                    os.path.splitext(image_name)[0] + ".txt"
                )

                with open(label_path, "w") as f:

                    for ann in annotations:

                        class_id, x1, y1, x2, y2 = ann

                        yolo_box = convert_to_yolo(
                            (display_w, display_h),
                            (original_w, original_h),
                            (x1, y1, x2, y2)
                        )

                        line = (
                            f"{class_id} "
                            f"{' '.join(map(str, yolo_box))}\n"
                        )

                        f.write(line)

                print(f"\nArquivo salvo:")
                print(label_path)

                print("\nConteúdo YOLO:")

                with open(label_path, "r") as f:
                    print(f.read())

            # =========================================
            # PRÓXIMA IMAGEM
            # =========================================

            elif key == ord("n"):

                if len(annotations) > 0:

                    display_h, display_w = current_image.shape[:2]

                    original_h, original_w = original_image.shape[:2]

                    label_path = os.path.join(
                        label_folder,
                        os.path.splitext(image_name)[0] + ".txt"
                    )

                    with open(label_path, "w") as f:

                        for ann in annotations:

                            class_id, x1, y1, x2, y2 = ann

                            yolo_box = convert_to_yolo(
                                (display_w, display_h),
                                (original_w, original_h),
                                (x1, y1, x2, y2)
                            )

                            line = (
                                f"{class_id} "
                                f"{' '.join(map(str, yolo_box))}\n"
                            )

                            f.write(line)

                    print(f"\nAuto save:")
                    print(label_path)

                break

            # =========================================
            # SAIR
            # =========================================

            elif key == 27:
                cv2.destroyAllWindows()
                exit()

        cv2.destroyAllWindows()

print("\nProcesso finalizado!")