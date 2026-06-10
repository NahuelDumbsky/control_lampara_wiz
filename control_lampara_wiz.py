import asyncio
from tkinter import ttk
import tracemalloc
from tkinter import *
from pywizlight import wizlight, PilotBuilder
from pywizlight.discovery import discover_lights

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
        "BTN_SCAN":  "#0f3460",
        "BTN_CONN":  "#12417a",
        "TOGGLE_BG": "#0f3460",
        "TOGGLE_FG": "#eaeaea",
        "TOGGLE_LBL": "Modo Claro",
        "COMBO_BG":  "#16213e",
        "COMBO_FG":  "#eaeaea",
        "COMBO_SEL": "#e94560",
        "COMBO_FIELD":"#0f3460",
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
        "BTN_SCAN":  "#dcdcec",
        "BTN_CONN":  "#d0f0d8",
        "TOGGLE_BG": "#dcdcec",
        "TOGGLE_FG": "#1a1a2e",
        "TOGGLE_LBL": "Modo Oscuro",
        "COMBO_BG":  "#ffffff",
        "COMBO_FG":  "#1a1a2e",
        "COMBO_SEL": "#c0392b",
        "COMBO_FIELD":"#ffffff",
    },
}

light   = None
found_lights = []


async def main():
    loop = asyncio.get_event_loop()
    current_theme = {"name": "dark"}

    def T(key):
        return THEMES[current_theme["name"]][key]

    def run_async(coro):
        asyncio.run_coroutine_threadsafe(coro, loop)

    # Ventana
    root = Tk()
    root.title("Wiz — Control de Lampara")
    root.geometry("440x600")
    root.resizable(False, False)
    root.configure(bg=T("BG"))

    # ttk Style para el Combobox
    style = ttk.Style(root)
    style.theme_use("default")

    def apply_combo_style():
        style.configure("Wiz.TCombobox",
                         fieldbackground=T("COMBO_FIELD"),
                         background=T("COMBO_BG"),
                         foreground=T("COMBO_FG"),
                         selectbackground=T("COMBO_SEL"),
                         selectforeground=T("FG"),
                         arrowcolor=T("FG"),
                         bordercolor=T("BG_PANEL"),
                         lightcolor=T("BG_PANEL"),
                         darkcolor=T("BG_PANEL"))
        style.map("Wiz.TCombobox",
                  fieldbackground=[("readonly", T("COMBO_FIELD"))],
                  foreground=[("readonly", T("COMBO_FG"))],
                  selectbackground=[("readonly", T("COMBO_SEL"))])

    # Corrutinas
    async def turn_on():
        await light.turn_on(PilotBuilder(rgb=(255, 255, 255), brightness=255))
        update_status("Encendida")

    async def turn_off():
        await light.turn_off()
        update_status("Apagada")

    async def white_warm():
        await light.turn_on(PilotBuilder(warm_white=255, brightness=255))
        update_status("Blanco Calido")

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

    async def scan_and_fill():
        global found_lights
        update_status("Buscando lamparas...")
        scan_btn.config(state=DISABLED)
        found_lights = await discover_lights()
        names = [lamp.ip for lamp in found_lights]
        lamp_selector["values"] = names
        if names:
            lamp_selector.current(0)
            update_status(f"{len(names)} lampara(s) encontrada(s)")
        else:
            update_status("No se encontraron lamparas")
        scan_btn.config(state=NORMAL)

    def connect_selected():
        global light
        idx = lamp_selector.current()
        if idx == -1:
            update_status("Selecciona una lampara primero")
            return
        light = found_lights[idx]
        update_status(f"Conectado a {light.ip}")
        # Habilitar controles
        for w in control_widgets:
            w.config(state=NORMAL)

    # Sistema de registro para tematizado
    all_widgets = []

    def reg(widget, kind):
        """Registra un widget para el repintado de tema."""
        all_widgets.append((widget, kind))
        return widget

    # Header
    header = reg(Frame(root, pady=10), "card_frame")
    header.pack(fill=X)

    reg(Label(header,
              text="💡  Control de Lampara Wiz",
              font=("Helvetica", 13, "bold")), "card_label_bold").pack()

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
    toggle_btn.pack(pady=(6, 0))

    # Sección de descubrimiento
    disc_frame = reg(Frame(header, pady=6), "card_frame")
    disc_frame.pack(fill=X, padx=16)

    reg(Label(disc_frame,
              text="Lampara",
              font=("Helvetica", 8, "bold")), "card_label_dim").grid(row=0, column=0, sticky=W, pady=(0,3))

    scan_btn = reg(
        Button(disc_frame,
               command=lambda: run_async(scan_and_fill()),
               text="Buscar",
               font=("Helvetica", 8, "bold"),
               relief=RAISED, bd=2,
               padx=10, pady=4,  
               cursor="hand2"),
        ("action_btn", "BTN_SCAN")
    )
    scan_btn.grid(row=0, column=1, sticky=E, padx=(8, 0), pady=(0,3))

    disc_frame.columnconfigure(0, weight=1)

    lamp_selector = ttk.Combobox(disc_frame, state="readonly",
                                  style="Wiz.TCombobox",
                                  font=("Helvetica", 9))
    lamp_selector.grid(row=1, column=0, columnspan=2, sticky=EW, pady=(0, 4))

    conn_btn = reg(
        Button(disc_frame,
               command=connect_selected,
               text="Conectar",
               font=("Helvetica", 8, "bold"),
               relief=RAISED, bd=2,
               padx=10, pady=4,
               cursor="hand2"),
        ("action_btn", "BTN_CONN")
    )
    conn_btn.grid(row=2, column=0, columnspan=2, sticky=EW)

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
              font=("Helvetica", 9, "bold")), "label_dim").pack(anchor=CENTER, pady=(0, 4))

    # Sliders RGB
    def make_scale(parent, label, trough_key):
        s = Scale(parent, from_=0, to=255, orient=HORIZONTAL, label=label,
                  length=230, highlightthickness=0, 
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

    color_btn = reg(Button(left_frame, text="Establecer Color",
               command=set_color, width=22,
               relief=FLAT, bd=0, pady=5,
               font=("Helvetica", 9, "bold")),
        ("action_btn", "BTN_COLOR"))
    color_btn.pack(pady=(8, 0))

    reg(Label(right_frame,
              text="Brillo",
              font=("Helvetica", 9, "bold")), "label_dim").pack(pady=(0, 4))

    brightness_slider = Scale(right_frame, from_=100, to=1, orient=VERTICAL,
                               length=175, highlightthickness=0,
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

    def mk_btn(text, btn_key, cmd, row, col):
        b = Button(btn_frame, text=text, command=cmd, width=17,
                   relief=RAISED, bd=0, pady=6, font=("Helvetica", 9))
        b.grid(row=row, column=col, padx=4, pady=3)
        reg(b, ("action_btn", btn_key))
        return b

    mk_btn("Encender", "BTN_ON",   lambda: run_async(turn_on()),    0, 0)
    mk_btn("Apagar", "BTN_OFF",  lambda: run_async(turn_off()),   0, 1)
    mk_btn("Blanco Calido", "BTN_WARM", lambda: run_async(white_warm()), 1, 0)
    mk_btn("Blanco Frío", "BTN_COLD", lambda: run_async(white_cold()), 1, 1)

    # Lista de controles que se habilitan al conectar
    control_widgets = [Red_slider, Green_slider, Blue_slider,
                       brightness_slider, color_btn]

    # Barra de estado
    status_label = reg(Label(root,
                             text="  ●  Sin conectar — usa Buscar",
                             anchor=W, padx=6,
                             font=("Courier", 9)),
                       "status_label")
    status_label.pack(fill=X, side=BOTTOM, ipady=6)

    def update_status(value):
        status_label.config(text=f"  ●  {value}")

    # Función de repintado
    def apply_theme():
        root.configure(bg=T("BG"))
        apply_combo_style()
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