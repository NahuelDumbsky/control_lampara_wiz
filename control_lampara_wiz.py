import asyncio
import tracemalloc
from tkinter import *
from pywizlight import wizlight, PilotBuilder

tracemalloc.start()

# Paletas de colores para modo claro y oscuro.
THEMES = {
    "dark": {
        "BG":        "#1a1a2e",
        "BG_PANEL":  "#16213e",
        "BG_CARD":   "#0f3460",
        "ACCENT":    "#e94560",
        "FG":        "#eaeaea",
        "FG_DIM":    "#8899aa",
        "TROUGH_R":  "#4a1a1a",
        "TROUGH_G":  "#1a4a1a",
        "TROUGH_B":  "#1a1a4a",
        "TROUGH_BR": "#2a2a1a",
        "BTN_ON":    "#2a2a0a",
        "BTN_OFF":   "#222233",
        "BTN_WARM":  "#3a2a0a",
        "BTN_COLD":  "#0a2a3a",
        "BTN_COLOR": "#1a1a3a",
        "TOGGLE_BG": "#0f3460",
        "TOGGLE_FG": "#eaeaea",
        "TOGGLE_LBL":"☀️  Modo Claro",
    },
    "light": {
        "BG":        "#f4f4f8",
        "BG_PANEL":  "#e8e8f0",
        "BG_CARD":   "#dcdcec",
        "ACCENT":    "#c0392b",
        "FG":        "#1a1a2e",
        "FG_DIM":    "#555577",
        "TROUGH_R":  "#ffcccc",
        "TROUGH_G":  "#ccffcc",
        "TROUGH_B":  "#ccccff",
        "TROUGH_BR": "#ffffcc",
        "BTN_ON":    "#fffacd",
        "BTN_OFF":   "#d0d0d0",
        "BTN_WARM":  "#ffe4b5",
        "BTN_COLD":  "#e0f0ff",
        "BTN_COLOR": "#e0e0ff",
        "TOGGLE_BG": "#dcdcec",
        "TOGGLE_FG": "#1a1a2e",
        "TOGGLE_LBL":"🌙  Modo Oscuro",
    },
}


async def main():
    light = wizlight("192.168.0.180")
    loop  = asyncio.get_event_loop()

    current_theme = {"name": "dark"}   # mutable ref para el toggle

    def T(key):
        return THEMES[current_theme["name"]][key]

    def run_async(coro):
        asyncio.run_coroutine_threadsafe(coro, loop)

    # Ventana
    root = Tk()
    root.title("Wiz — Control de Lámpara")
    root.geometry("440x520")
    root.resizable(False, False)
    root.configure(bg=T("BG"))

    # Corrutinas
    async def turn_on():
        await light.turn_on(PilotBuilder(rgb=(255, 255, 255), brightness=255))
        update_status("Encendida")

    async def turn_off():
        await light.turn_off()
        update_status("Apagada")

    async def white_warm():
        await light.turn_on(PilotBuilder(warm_white=255, brightness=255))
        update_status("Blanco Cálido")

    async def white_cold():
        await light.turn_on(PilotBuilder(cold_white=255, brightness=255))
        update_status("Blanco Frío")

    async def set_color_async(r, g, b):
        await light.turn_on(PilotBuilder(rgb=(r, g, b), brightness=255))
        update_status(f"Color  RGB({r}, {g}, {b})")

    async def set_brightness_async(value):
        b = int(value * 255 / 100)
        await light.turn_on(PilotBuilder(brightness=b))
        update_status(f"Brillo  {value}%")

    # Construcción de la UI
    # Guardamos referencias a todos los widgets que necesitan recolorearse
    all_widgets = []   # lista de (widget, tipo)  — se llena al crear cada uno

    def reg(widget, kind):
        """Registra un widget para el repintado de tema."""
        all_widgets.append((widget, kind))
        return widget

    # Header
    header = reg(Frame(root, pady=10), "card_frame")
    header.pack(fill=X)

    reg(Label(header,
              text="💡  Control de Lámpara Wiz",
              font=("Helvetica", 13, "bold")), "card_label_bold").pack()
    reg(Label(header,
              text="192.168.0.180",
              font=("Courier", 8)), "card_label_dim").pack()

    # Botón toggle — tipo tecla con relieve
    toggle_btn = reg(
        Button(header,
               text=T("TOGGLE_LBL"),
               font=("Helvetica", 8, "bold"),
               relief=RAISED, bd=2,
               padx=8, pady=3,
               cursor="hand2"),
        "toggle_btn"
    )
    toggle_btn.pack(pady=(6, 2))

    # Body
    body = reg(Frame(root, padx=12, pady=10), "bg_frame")
    body.pack(fill=BOTH, expand=True)

    left_frame = reg(Frame(body), "bg_frame")
    left_frame.pack(side=LEFT, fill=BOTH, expand=True)

    right_frame = reg(Frame(body, padx=8), "bg_frame")
    right_frame.pack(side=RIGHT, fill=Y)

    # Labels de sección
    reg(Label(left_frame,
              text="Color RGB",
              font=("Helvetica", 9, "bold")), "label_dim").pack(anchor=W, pady=(0, 4))

    # Sliders RGB
    def make_scale(parent, label, trough_key):
        s = Scale(parent, from_=0, to=255, orient=HORIZONTAL, label=label,
                  length=250, highlightthickness=0,
                  font=("Helvetica", 8))
        s.set(255)
        s.pack(pady=2)
        reg(s, ("scale", trough_key))
        return s

    Red_slider   = make_scale(left_frame, "Rojo",  "TROUGH_R")
    Green_slider = make_scale(left_frame, "Verde", "TROUGH_G")
    Blue_slider  = make_scale(left_frame, "Azul",  "TROUGH_B")

    def set_color():
        r, g, b = Red_slider.get(), Green_slider.get(), Blue_slider.get()
        run_async(set_color_async(r, g, b))

    reg(Button(left_frame, text="Establecer Color",
               command=set_color, width=22,
               relief=FLAT, bd=0, pady=5,
               font=("Helvetica", 9, "bold")),
        ("action_btn", "BTN_COLOR")).pack(pady=(8, 0))

    # Slider Brillo
    reg(Label(right_frame,
              text="Brillo",
              font=("Helvetica", 9, "bold")), "label_dim").pack(pady=(0, 4))

    brightness_slider = Scale(right_frame, from_=100, to=1, orient=VERTICAL,
                               length=190, highlightthickness=0,
                               font=("Helvetica", 8))
    brightness_slider.set(100)
    brightness_slider.pack()
    reg(brightness_slider, ("scale", "TROUGH_BR"))

    def on_brightness_release(event):
        run_async(set_brightness_async(brightness_slider.get()))
    brightness_slider.bind("<ButtonRelease-1>", on_brightness_release)

    # Botones de acción
    btn_frame = reg(Frame(root, pady=4), "bg_frame")
    btn_frame.pack()

    action_buttons = []  # [(widget, BTN_KEY)]

    def mk_btn(text, btn_key, cmd, row, col):
        b = Button(btn_frame, text=text, command=cmd, width=17,
                   relief=FLAT, bd=0, pady=6,
                   font=("Helvetica", 9))
        b.grid(row=row, column=col, padx=4, pady=3)
        action_buttons.append((b, btn_key))
        reg(b, ("action_btn", btn_key))

    mk_btn("💡  Encender",     "BTN_ON",   lambda: run_async(turn_on()),    0, 0)
    mk_btn("🌑  Apagar",        "BTN_OFF",  lambda: run_async(turn_off()),   0, 1)
    mk_btn("🌅  Blanco Cálido", "BTN_WARM", lambda: run_async(white_warm()), 1, 0)
    mk_btn("❄  Blanco Frío",  "BTN_COLD", lambda: run_async(white_cold()), 1, 1)

    # Barra de estado
    status_label = reg(Label(root,
                             text="  ●  Apagada",
                             anchor=W, padx=6,
                             font=("Courier", 9)),
                       "status_label")
    status_label.pack(fill=X, side=BOTTOM, ipady=6)

    def update_status(value):
        status_label.config(text=f"  ●  {value}")

    # Función de repintado
    def apply_theme():
        root.configure(bg=T("BG"))
        for widget, kind in all_widgets:
            if kind == "card_frame":
                widget.configure(bg=T("BG_CARD"))
            elif kind == "bg_frame":
                widget.configure(bg=T("BG"))
            elif kind == "card_label_bold":
                widget.configure(bg=T("BG_CARD"), fg=T("FG"))
            elif kind == "card_label_dim":
                widget.configure(bg=T("BG_CARD"), fg=T("FG_DIM"))
            elif kind == "label_dim":
                widget.configure(bg=T("BG"), fg=T("FG_DIM"))
            elif kind == "status_label":
                widget.configure(bg=T("BG_CARD"), fg=T("ACCENT"))
            elif kind == "toggle_btn":
                widget.configure(
                    bg=T("TOGGLE_BG"), fg=T("TOGGLE_FG"),
                    activebackground=T("ACCENT"), activeforeground=T("FG"),
                    text=T("TOGGLE_LBL"),
                )
            elif isinstance(kind, tuple) and kind[0] == "scale":
                trough_key = kind[1]
                widget.configure(
                    bg=T("BG_PANEL"), fg=T("FG"),
                    troughcolor=T(trough_key),
                    activebackground=T("ACCENT"),
                )
            elif isinstance(kind, tuple) and kind[0] == "action_btn":
                btn_key = kind[1]
                widget.configure(
                    bg=T(btn_key), fg=T("FG"),
                    activebackground=T("ACCENT"), activeforeground=T("FG"),
                )

    # Aplicar tema inicial
    apply_theme()

    # Toggle callback
    def toggle_theme():
        current_theme["name"] = "light" if current_theme["name"] == "dark" else "dark"
        apply_theme()

    toggle_btn.configure(command=toggle_theme)

    # Loop tkinter
    async def tk_update():
        while True:
            root.update()
            await asyncio.sleep(0.05)

    await tk_update()


if __name__ == "__main__":
    asyncio.run(main())