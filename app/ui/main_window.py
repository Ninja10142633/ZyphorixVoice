"""
Janela principal do ZyphorixVoice.

Define o layout, componentes visuais e lógica de controle da interface
gráfica usando CustomTkinter com tema escuro e estilo moderno.
"""

import tkinter as tk
from pathlib import Path
from typing import Callable

import customtkinter as ctk
from PIL import Image

from app.config.settings import settings
from app.utils.logger import get_logger


logger = get_logger("ui.main_window")

_ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"

# Paleta de cores
_COLOR_BG = "#0d0d1a"
_COLOR_SURFACE = "#14142b"
_COLOR_PRIMARY = "#a855f7"
_COLOR_PRIMARY_HOVER = "#9333ea"
_COLOR_DANGER = "#ef4444"
_COLOR_DANGER_HOVER = "#dc2626"
_COLOR_TEXT = "#e2e8f0"
_COLOR_SUBTEXT = "#94a3b8"
_COLOR_BORDER = "#1e1e3f"
_COLOR_STATUS_IDLE = "#64748b"
_COLOR_STATUS_RUNNING = "#22c55e"


class MainWindow(ctk.CTk):
    """
    Janela principal da aplicação.

    Responsável por renderizar a interface e expor callbacks
    para os botões de Iniciar e Parar.
    """

    def __init__(
        self,
        on_start: Callable[[], None] | None = None,
        on_stop: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self._on_start = on_start
        self._on_stop = on_stop
        self._is_running = False

        self._configure_window()
        self._build_ui()

        logger.info("Janela principal inicializada.")

    # ──────────────────────────────────────────────
    # Configuração inicial
    # ──────────────────────────────────────────────

    def _configure_window(self) -> None:
        """Define título, tamanho, tema e cor de fundo da janela."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(f"{settings.app.app_name}  v{settings.app.version}")
        self.geometry("480x640")
        self.resizable(False, False)
        self.configure(fg_color=_COLOR_BG)

        # Centraliza a janela na tela
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 480) // 2
        y = (self.winfo_screenheight() - 640) // 2
        self.geometry(f"480x640+{x}+{y}")

    # ──────────────────────────────────────────────
    # Construção da interface
    # ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Monta todos os widgets da interface."""
        self._build_header()
        self._build_microphone_info()
        self._build_status_panel()
        self._build_controls()
        self._build_footer()

    def _build_header(self) -> None:
        """Seção do topo: logo + nome do app."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(36, 0))

        # Logo
        logo_path = _ASSETS_DIR / "logo.png"
        if logo_path.exists():
            pil_image = Image.open(logo_path)
            logo_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(120, 120))
            logo_label = ctk.CTkLabel(header_frame, image=logo_img, text="")
            logo_label.pack()
        else:
            placeholder = ctk.CTkLabel(
                header_frame,
                text="🎙",
                font=ctk.CTkFont(size=72),
                text_color=_COLOR_PRIMARY,
            )
            placeholder.pack()
            logger.warning("Logo não encontrada em assets/logo.png. Usando placeholder.")

        # Nome do app
        ctk.CTkLabel(
            header_frame,
            text="ZyphorixVoice",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=_COLOR_TEXT,
        ).pack(pady=(12, 0))

        ctk.CTkLabel(
            header_frame,
            text="Tradutor de Voz em Tempo Real",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=_COLOR_SUBTEXT,
        ).pack(pady=(4, 0))

        # Separador
        separator = ctk.CTkFrame(self, height=1, fg_color=_COLOR_BORDER)
        separator.pack(fill="x", padx=40, pady=(24, 0))

    def _build_microphone_info(self) -> None:
        """Painel informativo do microfone selecionado."""
        mic_frame = ctk.CTkFrame(self, fg_color=_COLOR_SURFACE, corner_radius=12)
        mic_frame.pack(fill="x", padx=40, pady=(20, 0))

        ctk.CTkLabel(
            mic_frame,
            text="🎤  MICROFONE",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=_COLOR_SUBTEXT,
        ).pack(anchor="w", padx=16, pady=(12, 2))

        self._mic_label = ctk.CTkLabel(
            mic_frame,
            text=settings.audio.default_microphone,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=_COLOR_TEXT,
            wraplength=360,
            anchor="w",
            justify="left",
        )
        self._mic_label.pack(anchor="w", padx=16, pady=(0, 12))

    def _build_status_panel(self) -> None:
        """Painel de status da aplicação."""
        status_frame = ctk.CTkFrame(self, fg_color=_COLOR_SURFACE, corner_radius=12)
        status_frame.pack(fill="x", padx=40, pady=(12, 0))

        ctk.CTkLabel(
            status_frame,
            text="⬤  STATUS",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color=_COLOR_SUBTEXT,
        ).pack(anchor="w", padx=16, pady=(12, 2))

        self._status_label = ctk.CTkLabel(
            status_frame,
            text="Aguardando...",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=_COLOR_STATUS_IDLE,
        )
        self._status_label.pack(anchor="w", padx=16, pady=(0, 12))

    def _build_controls(self) -> None:
        """Botões de Iniciar e Parar."""
        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.pack(pady=(28, 0))

        self._btn_start = ctk.CTkButton(
            controls_frame,
            text="▶  Iniciar",
            width=160,
            height=48,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=_COLOR_PRIMARY,
            hover_color=_COLOR_PRIMARY_HOVER,
            command=self._handle_start,
        )
        self._btn_start.grid(row=0, column=0, padx=10)

        self._btn_stop = ctk.CTkButton(
            controls_frame,
            text="■  Parar",
            width=160,
            height=48,
            corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=_COLOR_SURFACE,
            hover_color=_COLOR_DANGER_HOVER,
            text_color=_COLOR_SUBTEXT,
            border_width=1,
            border_color=_COLOR_BORDER,
            state="disabled",
            command=self._handle_stop,
        )
        self._btn_stop.grid(row=0, column=1, padx=10)

    def _build_footer(self) -> None:
        """Rodapé com versão."""
        ctk.CTkLabel(
            self,
            text=f"v{settings.app.version}  •  ZyphorixVoice",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=_COLOR_BORDER,
        ).pack(side="bottom", pady=16)

    # ──────────────────────────────────────────────
    # Handlers de eventos
    # ──────────────────────────────────────────────

    def _handle_start(self) -> None:
        """Callback interno do botão Iniciar."""
        if self._is_running:
            return

        self._is_running = True
        self._update_status("Ativo — traduzindo...", running=True)
        self._btn_start.configure(state="disabled", fg_color=_COLOR_SURFACE, text_color=_COLOR_SUBTEXT)
        self._btn_stop.configure(state="normal", fg_color=_COLOR_DANGER, text_color=_COLOR_TEXT)

        logger.info("Tradução iniciada pelo usuário.")

        if self._on_start:
            self._on_start()

    def _handle_stop(self) -> None:
        """Callback interno do botão Parar."""
        if not self._is_running:
            return

        self._is_running = False
        self._update_status("Parado.", running=False)
        self._btn_start.configure(state="normal", fg_color=_COLOR_PRIMARY, text_color=_COLOR_TEXT)
        self._btn_stop.configure(state="disabled", fg_color=_COLOR_SURFACE, text_color=_COLOR_SUBTEXT)

        logger.info("Tradução parada pelo usuário.")

        if self._on_stop:
            self._on_stop()

    # ──────────────────────────────────────────────
    # Métodos públicos para atualização de estado
    # ──────────────────────────────────────────────

    def _update_status(self, message: str, running: bool = False) -> None:
        """Atualiza o texto e cor do campo de status."""
        color = _COLOR_STATUS_RUNNING if running else _COLOR_STATUS_IDLE
        self._status_label.configure(text=message, text_color=color)

    def set_microphone(self, name: str) -> None:
        """Atualiza o nome do microfone exibido na interface."""
        self._mic_label.configure(text=name)

    def set_status(self, message: str, running: bool = False) -> None:
        """API pública para atualizar o status externamente."""
        self._update_status(message, running)
