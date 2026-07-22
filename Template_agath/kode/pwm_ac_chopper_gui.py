import csv
import queue
import threading
import time
from collections import deque
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import serial
from serial.tools import list_ports


BAUDRATE = 115200
CSV_LOG_INTERVAL_SECONDS = 0.5
SENSOR_MOVING_AVERAGE_SAMPLES = 15
CSV_HEADER = [
    "pc_timestamp",
    "stm32_ms",
    "adc_raw",
    "adc_voltage_v",
    "sensor_voltage_v",
    "pressure_bar",
    "duty_percent",
    "frequency_hz",
    "estimated_output_rms_v",
    "jsy_online",
    "jsy_voltage_rms_v",
    "jsy_current_rms_a",
    "jsy_voltage_raw_v",
    "jsy_current_raw_a",
    "jsy_active_power_w",
    "jsy_power_factor",
    "jsy_energy_kwh",
    "jsy_error_count",
    "nn_mode",
    "nn_duty_percent",
    "valve_open_count",
    "valve_state_label",
    "valve_phase",
    "setpoint_bar",
    "episode_id",
    "is_decision",
    "event",
]

# === Auto data-collection (closed-loop manual policy / behavior cloning) ===
COLLECT_DEFAULT_DUTY_MIN = 70.0  # lantai duty (bisa diatur live di GUI)
COLLECT_DUTY_MAX = 95.0          # plafon duty
COLLECT_DEFAULT_SETPOINT = 0.30  # bar
COLLECT_DEFAULT_INTERVAL = 3.0   # detik antar-keputusan


def policy_step(error):
    """Kebijakan proporsional tetap (4 level). error = setpoint - pressure.

    Output = perubahan duty (dDuty) sebelum clamp. JANGAN diubah di tengah
    pengambilan data -- konsistensi aturan ini yang membuat MLP bisa belajar.
    """
    if error > 0.08:
        return 3
    if error > 0.05:
        return 2
    if error > 0.02:
        return 1
    if error >= -0.02:
        return 0          # deadband -> tahan
    if error >= -0.05:
        return -1
    if error >= -0.08:
        return -2
    return -3


class SerialWorker:
    def __init__(self, line_queue):
        self.line_queue = line_queue
        self.serial_port = None
        self.thread = None
        self.running = False

    def connect(self, port):
        self.disconnect()
        self.serial_port = serial.Serial(port, BAUDRATE, timeout=0.2)
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def disconnect(self):
        self.running = False
        if self.serial_port is not None:
            try:
                self.serial_port.close()
            except serial.SerialException:
                pass
        self.serial_port = None

    def send(self, command):
        if self.serial_port is None or not self.serial_port.is_open:
            raise RuntimeError("Serial port is not connected")
        self.serial_port.write((command.strip() + "\n").encode("ascii"))

    def _read_loop(self):
        while self.running and self.serial_port is not None:
            try:
                raw = self.serial_port.readline()
            except serial.SerialException as exc:
                self.line_queue.put(("ERROR", str(exc)))
                break
            if not raw:
                continue
            line = raw.decode("ascii", errors="replace").strip()
            if line:
                self.line_queue.put(("LINE", line))


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PWM AC Chopper Controller")
        self.geometry("980x620")
        self.minsize(900, 560)

        self.line_queue = queue.Queue()
        self.serial_worker = SerialWorker(self.line_queue)
        self.csv_file = None
        self.csv_writer = None
        self.last_csv_log_time = 0.0
        self.sensor_average_buffers = {
            "adc_voltage_v": deque(maxlen=SENSOR_MOVING_AVERAGE_SAMPLES),
            "sensor_voltage_v": deque(maxlen=SENSOR_MOVING_AVERAGE_SAMPLES),
            "pressure_bar": deque(maxlen=SENSOR_MOVING_AVERAGE_SAMPLES),
        }

        self.port_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Disconnected")
        self.duty_var = tk.DoubleVar(value=50.0)
        self.freq_var = tk.IntVar(value=5000)
        self.csv_path_var = tk.StringVar(value=str(Path.cwd() / "pwm_ac_chopper_log.csv"))
        # Setpoint NN (adjustable via GUI, default 0.30 bar)
        self.setpoint_var = tk.DoubleVar(value=0.30)
        self.setpoint_status_var = tk.StringVar(value="(setpoint: 0.30 bar)")
        # Display setpoint & error (di-update dari telemetry STM32)
        self.setpoint_display_var = tk.StringVar(value="0.30 bar")
        self.error_display_var = tk.StringVar(value="+0.000 bar")
        # Warna error: hijau jika kecil, merah jika besar
        self.error_color = "green"
        self.valve_open_count = "-"
        self.valve_state_label = "Belum ditandai"
        self.valve_phase = "unset"
        self.valve_marker_var = tk.StringVar(value="Keran: belum ditandai")
        # Mode controller: 0=Manual, 1=NN
        self.controller_mode = tk.StringVar(value="MANUAL")
        self.nn_duty_var = tk.DoubleVar(value=0.0)

        # === Auto data-collection (closed-loop manual policy) ===
        self.episode_id = 1
        self.auto_collect_running = False
        self.latest_row = None          # snapshot telemetry terakhir (untuk keputusan)
        self._decision_after_id = None
        self.collect_setpoint_var = tk.DoubleVar(value=COLLECT_DEFAULT_SETPOINT)
        self.collect_interval_var = tk.DoubleVar(value=COLLECT_DEFAULT_INTERVAL)
        self.collect_duty_min_var = tk.DoubleVar(value=COLLECT_DEFAULT_DUTY_MIN)
        self.episode_var = tk.StringVar(value="Episode: 1")
        self.collect_status_var = tk.StringVar(value="Auto-collect: OFF")
        # Penanda event untuk uji NN (mis. ganti setpoint / gangguan keran)
        self.event_marker = ""
        self.event_var = tk.StringVar(value="")

        self.telemetry_vars = {
            "adc_raw": tk.StringVar(value="-"),
            "adc_voltage": tk.StringVar(value="-"),
            "sensor_voltage": tk.StringVar(value="-"),
            "pressure": tk.StringVar(value="-"),
            "duty": tk.StringVar(value="-"),
            "frequency": tk.StringVar(value="-"),
            "rms": tk.StringVar(value="-"),
            "jsy_status": tk.StringVar(value="-"),
            "jsy_voltage": tk.StringVar(value="-"),
            "jsy_current": tk.StringVar(value="-"),
            "jsy_power": tk.StringVar(value="-"),
            "jsy_pf": tk.StringVar(value="-"),
            "jsy_energy": tk.StringVar(value="-"),
            "jsy_errors": tk.StringVar(value="-"),
            "nn_duty": tk.StringVar(value="-"),
        }

        self._build_ui()
        self.refresh_ports()
        self.after(50, self.process_queue)

    def _build_ui(self):
        # === Scrollable canvas wrapper ===
        # Bungkus konten dengan Canvas + Scrollbar agar bisa di-scroll
        # saat window lebih kecil dari konten (terutama Serial Log)
        canvas_container = ttk.Frame(self)
        canvas_container.pack(fill="both", expand=True)

        self._canvas = tk.Canvas(canvas_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            canvas_container, orient="vertical", command=self._canvas.yview
        )
        outer = ttk.Frame(self._canvas, padding=12)
        outer.bind(
            "<Configure>",
            lambda e: self._canvas.configure(
                scrollregion=self._canvas.bbox("all")
            ),
        )
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=outer, anchor="nw"
        )
        self._canvas.configure(yscrollcommand=scrollbar.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mouse wheel untuk scroll
        def _on_mousewheel(event):
            # event.delta: positive = scroll up, negative = scroll down
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Linux scroll (Button-4/5)
        self._canvas.bind_all("<Button-4>", lambda e: self._canvas.yview_scroll(-1, "units"))
        self._canvas.bind_all("<Button-5>", lambda e: self._canvas.yview_scroll(1, "units"))

        # Bind lebar canvas ke lebar window (agar konten tidak overflow horizontal)
        def _on_canvas_configure(event):
            self._canvas.itemconfig(
                self._canvas_window, width=event.width
            )
        self._canvas.bind("<Configure>", _on_canvas_configure)

        connection = ttk.LabelFrame(outer, text="Connection", padding=10)
        connection.pack(fill="x")

        ttk.Label(connection, text="Port").grid(row=0, column=0, sticky="w")
        self.port_combo = ttk.Combobox(connection, textvariable=self.port_var, width=24)
        self.port_combo.grid(row=0, column=1, padx=8, sticky="w")
        ttk.Button(connection, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=4)
        self.connect_button = ttk.Button(connection, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=3, padx=4)
        ttk.Label(connection, textvariable=self.status_var).grid(row=0, column=4, padx=12, sticky="w")
        connection.columnconfigure(5, weight=1)

        controls = ttk.LabelFrame(outer, text="PWM Control", padding=10)
        controls.pack(fill="x", pady=10)

        ttk.Label(controls, text="Duty Cycle (%)").grid(row=0, column=0, sticky="w")
        duty_scale = ttk.Scale(
            controls,
            from_=0.0,
            to=95.0,
            variable=self.duty_var,
            command=lambda _: self._sync_duty_label(),
        )
        duty_scale.grid(row=0, column=1, padx=8, sticky="ew")
        self.duty_label = ttk.Label(controls, width=8, text="50.00")
        self.duty_label.grid(row=0, column=2, sticky="w")

        duty_adjust = ttk.Frame(controls)
        duty_adjust.grid(row=1, column=1, columnspan=2, padx=8, sticky="w")
        ttk.Button(duty_adjust, text="-5", width=4, command=lambda: self.adjust_duty(-5.0)).pack(side="left", padx=2)
        ttk.Button(duty_adjust, text="-1", width=4, command=lambda: self.adjust_duty(-1.0)).pack(side="left", padx=2)
        ttk.Spinbox(
            duty_adjust,
            from_=0.0,
            to=95.0,
            increment=0.1,
            textvariable=self.duty_var,
            width=8,
            format="%.2f",
            command=self._sync_duty_label,
        ).pack(side="left", padx=4)
        ttk.Button(duty_adjust, text="+1", width=4, command=lambda: self.adjust_duty(1.0)).pack(side="left", padx=2)
        ttk.Button(duty_adjust, text="+5", width=4, command=lambda: self.adjust_duty(5.0)).pack(side="left", padx=2)
        ttk.Button(duty_adjust, text="20", width=4, command=lambda: self.set_duty_value(20.0)).pack(side="left", padx=(10, 2))
        ttk.Button(duty_adjust, text="25", width=4, command=lambda: self.set_duty_value(25.0)).pack(side="left", padx=2)
        ttk.Button(duty_adjust, text="50", width=4, command=lambda: self.set_duty_value(50.0)).pack(side="left", padx=2)
        ttk.Button(duty_adjust, text="95", width=4, command=lambda: self.set_duty_value(95.0)).pack(side="left", padx=2)

        ttk.Label(controls, text="Frequency (Hz)").grid(row=2, column=0, sticky="w", pady=8)
        ttk.Spinbox(controls, from_=100, to=50000, increment=100, textvariable=self.freq_var, width=12).grid(
            row=2, column=1, padx=8, sticky="w"
        )

        ttk.Button(controls, text="Apply Duty", command=self.apply_duty).grid(row=0, column=3, padx=4)
        ttk.Button(controls, text="Apply Frequency", command=self.apply_frequency).grid(row=2, column=3, padx=4)
        ttk.Button(controls, text="Apply Both", command=self.apply_both).grid(row=0, column=4, padx=4)
        ttk.Button(controls, text="Stop PWM", command=self.stop_pwm).grid(row=2, column=4, padx=4)
        ttk.Button(controls, text="Scan JSY", command=self.scan_jsy).grid(row=0, column=5, padx=4)
        controls.columnconfigure(1, weight=1)

        # === Controller Mode Section (NN vs Manual) ===
        mode_frame = ttk.LabelFrame(outer, text="Controller Mode (Manual / NN)", padding=10)
        mode_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(mode_frame, text="Pilih mode lalu klik Apply:").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )

        # Radio button (lebih reliable dari command=callback)
        ttk.Radiobutton(
            mode_frame, text="Manual (Open-Loop)",
            variable=self.controller_mode, value="MANUAL",
        ).grid(row=1, column=0, padx=4, pady=4, sticky="w")

        ttk.Radiobutton(
            mode_frame, text="NN (Closed-Loop)",
            variable=self.controller_mode, value="NN",
        ).grid(row=1, column=1, padx=4, pady=4, sticky="w")

        # Tombol "Apply Mode" terpisah (seperti tombol Apply Duty/Apply Both)
        ttk.Button(
            mode_frame, text="Apply Mode",
            command=self.apply_mode,
        ).grid(row=1, column=2, padx=8, pady=4)

        ttk.Button(
            mode_frame, text="Query Mode",
            command=self.query_mode,
        ).grid(row=1, column=3, padx=4, pady=4)

        # Display NN output & status
        ttk.Label(mode_frame, text="NN Output:").grid(
            row=0, column=4, padx=(20, 4), sticky="e"
        )
        ttk.Label(
            mode_frame,
            textvariable=self.telemetry_vars["nn_duty"],
            width=10, font=("TkDefaultFont", 10, "bold"),
        ).grid(row=0, column=5, padx=4, sticky="w")

        self.mode_status_label = ttk.Label(
            mode_frame, text="Status: MANUAL",
            foreground="blue", font=("TkDefaultFont", 10, "bold"),
        )
        self.mode_status_label.grid(row=1, column=4, columnspan=2, padx=(20, 4), sticky="w")
        mode_frame.columnconfigure(6, weight=1)

        # === Setpoint Control (Adjustable via GUI) ===
        # Default 0.50 bar, range 0.0 - 1.5 bar
        ttk.Separator(mode_frame, orient="horizontal").grid(
            row=2, column=0, columnspan=7, sticky="ew", pady=8
        )
        ttk.Label(mode_frame, text="Setpoint NN (bar):").grid(
            row=3, column=0, padx=4, pady=4, sticky="w"
        )
        ttk.Spinbox(
            mode_frame, from_=0.0, to=1.5, increment=0.05,
            textvariable=self.setpoint_var, width=8, format="%.2f",
        ).grid(row=3, column=1, padx=4, pady=4, sticky="w")
        ttk.Button(
            mode_frame, text="Apply Setpoint",
            command=self.apply_setpoint,
        ).grid(row=3, column=2, padx=8, pady=4, sticky="w")
        ttk.Button(
            mode_frame, text="Query Setpoint",
            command=self.query_setpoint,
        ).grid(row=3, column=3, padx=4, pady=4, sticky="w")
        ttk.Label(
            mode_frame, textvariable=self.setpoint_status_var,
            foreground="gray",
        ).grid(row=3, column=4, columnspan=3, padx=(20, 4), sticky="w")

        valve = ttk.LabelFrame(outer, text="Valve / Keran Marker untuk CSV", padding=10)
        valve.pack(fill="x", pady=(0, 10))
        ttk.Label(valve, textvariable=self.valve_marker_var).grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 6))

        stable_buttons = [
            ("4", "4"),
            ("3 1/2", "3.5"),
            ("3", "3"),
            ("2 1/2", "2.5"),
            ("2", "2"),
            ("1 1/2", "1.5"),
            ("1", "1"),
            ("1/2", "0.5"),
            ("0", "0"),
        ]
        for idx, (label, value) in enumerate(stable_buttons):
            row = 1 + (idx // 5)
            col = idx % 5
            ttk.Button(
                valve,
                text=f"{label} keran stabil",
                command=lambda v=value, l=label: self.set_valve_marker(v, "stable", l),
            ).grid(row=row, column=col, padx=3, pady=2, sticky="ew")

        ttk.Button(
            valve,
            text="Transisi tutup 4->0",
            command=lambda: self.set_valve_marker("4->0", "transition_close"),
        ).grid(row=3, column=0, columnspan=2, padx=3, pady=2, sticky="ew")
        ttk.Button(
            valve,
            text="Transisi buka 0->4",
            command=lambda: self.set_valve_marker("0->4", "transition_open"),
        ).grid(row=3, column=2, columnspan=2, padx=3, pady=2, sticky="ew")
        ttk.Button(
            valve,
            text="Transisi manual",
            command=lambda: self.set_valve_marker("manual", "transition_manual"),
        ).grid(row=4, column=0, columnspan=2, padx=3, pady=2, sticky="ew")
        ttk.Button(
            valve,
            text="Reset marker",
            command=self.reset_valve_marker,
        ).grid(row=4, column=2, columnspan=2, padx=3, pady=2, sticky="ew")

        # Penanda event (untuk uji NN: tandai momen ganti setpoint / gangguan)
        ttk.Label(valve, text="Event CSV:").grid(row=5, column=0, padx=3, pady=(8, 2), sticky="e")
        ttk.Entry(valve, textvariable=self.event_var).grid(
            row=5, column=1, columnspan=2, padx=3, pady=(8, 2), sticky="ew"
        )
        ttk.Button(valve, text="Tandai", command=self.set_event).grid(
            row=5, column=3, padx=3, pady=(8, 2), sticky="ew"
        )
        ttk.Button(valve, text="Hapus", command=self.clear_event).grid(
            row=5, column=4, padx=3, pady=(8, 2), sticky="ew"
        )
        for col in range(5):
            valve.columnconfigure(col, weight=1)

        # === Auto Data Collection (Closed-Loop Manual Policy) ===
        collect = ttk.LabelFrame(
            outer,
            text="Auto Data Collection (Closed-Loop Manual / Behavior Cloning)",
            padding=10,
        )
        collect.pack(fill="x", pady=(0, 10))

        ttk.Label(collect, text="Setpoint (bar)").grid(row=0, column=0, sticky="w")
        ttk.Spinbox(
            collect, from_=0.0, to=1.5, increment=0.01,
            textvariable=self.collect_setpoint_var, width=8, format="%.2f",
        ).grid(row=0, column=1, padx=6, sticky="w")

        ttk.Label(collect, text="Interval (s)").grid(
            row=0, column=2, sticky="w", padx=(16, 0)
        )
        ttk.Spinbox(
            collect, from_=1.0, to=10.0, increment=0.5,
            textvariable=self.collect_interval_var, width=6, format="%.1f",
        ).grid(row=0, column=3, padx=6, sticky="w")

        ttk.Label(collect, text="Duty min (%)").grid(
            row=0, column=4, sticky="w", padx=(16, 0)
        )
        ttk.Spinbox(
            collect, from_=40.0, to=95.0, increment=1.0,
            textvariable=self.collect_duty_min_var, width=6, format="%.0f",
        ).grid(row=0, column=5, padx=6, sticky="w")

        self.auto_collect_button = ttk.Button(
            collect, text="Start Auto-Collect", command=self.toggle_auto_collect
        )
        self.auto_collect_button.grid(row=0, column=6, padx=10)

        ttk.Label(
            collect, textvariable=self.collect_status_var,
            foreground="blue", font=("TkDefaultFont", 10, "bold"),
        ).grid(row=0, column=7, padx=10, sticky="w")

        ttk.Separator(collect, orient="horizontal").grid(
            row=1, column=0, columnspan=8, sticky="ew", pady=8
        )

        ttk.Label(
            collect, textvariable=self.episode_var,
            font=("TkDefaultFont", 11, "bold"),
        ).grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Button(
            collect, text="Episode Baru (+1)", command=self.new_episode
        ).grid(row=2, column=2, padx=6, sticky="w")
        ttk.Label(
            collect,
            text="Klik 'Episode Baru' tiap kali Anda set ulang duty ke nilai awal (loncat). "
                 "JANGAN klik saat hanya ubah keran di tengah kejar.",
            font=("TkDefaultFont", 9, "italic"), foreground="gray",
        ).grid(row=3, column=0, columnspan=8, sticky="w", pady=(4, 0))
        ttk.Label(
            collect,
            text="Aturan dDuty: err>0.08->+3 | >0.05->+2 | >0.02->+1 | +/-0.02->0 | "
                 "<-0.02->-1 | <-0.05->-2 | <-0.08->-3   (clamp Duty min-95%)",
            font=("TkDefaultFont", 9), foreground="gray",
        ).grid(row=4, column=0, columnspan=8, sticky="w", pady=(2, 0))

        collect.columnconfigure(7, weight=1)

        telemetry = ttk.LabelFrame(outer, text="Telemetry", padding=10)
        telemetry.pack(fill="x")

        labels = [
            ("ADC Raw", "adc_raw"),
            ("ADC Voltage", "adc_voltage"),
            ("Sensor Voltage", "sensor_voltage"),
            ("Pressure", "pressure"),
            ("Duty", "duty"),
            ("Frequency", "frequency"),
            ("Est. Output RMS", "rms"),
            ("JSY Status", "jsy_status"),
            ("JSY Voltage", "jsy_voltage"),
            ("JSY Current", "jsy_current"),
            ("JSY Power", "jsy_power"),
            ("Power Factor", "jsy_pf"),
            ("Energy", "jsy_energy"),
            ("JSY Errors", "jsy_errors"),
        ]
        for idx, (label, key) in enumerate(labels):
            row = idx // 4
            col = (idx % 4) * 2
            ttk.Label(telemetry, text=label).grid(row=row, column=col, sticky="w", padx=(0, 4), pady=4)
            ttk.Label(telemetry, textvariable=self.telemetry_vars[key], width=18).grid(
                row=row, column=col + 1, sticky="w", padx=(0, 12), pady=4
            )

        # === Target vs Actual (NN Performance) ===
        # Tampil di frame terpisah di bawah telemetry utama
        perf_frame = ttk.LabelFrame(outer, text="NN Controller Performance (Target vs Actual)", padding=10)
        perf_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(perf_frame, text="Target (Setpoint):",
                  font=("TkDefaultFont", 10, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 4), pady=4
        )
        ttk.Label(perf_frame, textvariable=self.setpoint_display_var,
                  font=("TkDefaultFont", 11, "bold"), foreground="blue").grid(
            row=0, column=1, sticky="w", padx=4, pady=4
        )

        ttk.Label(perf_frame, text="Actual Pressure:",
                  font=("TkDefaultFont", 10, "bold")).grid(
            row=0, column=2, sticky="w", padx=(20, 4), pady=4
        )
        ttk.Label(perf_frame, textvariable=self.telemetry_vars["pressure"],
                  font=("TkDefaultFont", 11, "bold"), foreground="darkgreen").grid(
            row=0, column=3, sticky="w", padx=4, pady=4
        )

        ttk.Label(perf_frame, text="Error (Target - Actual):",
                  font=("TkDefaultFont", 10, "bold")).grid(
            row=1, column=0, sticky="w", padx=(0, 4), pady=4
        )
        self.error_label_widget = ttk.Label(
            perf_frame, textvariable=self.error_display_var,
            font=("TkDefaultFont", 11, "bold"), foreground=self.error_color,
        )
        self.error_label_widget.grid(row=1, column=1, sticky="w", padx=4, pady=4)

        ttk.Label(perf_frame, text="NN Output (Duty):",
                  font=("TkDefaultFont", 10, "bold")).grid(
            row=1, column=2, sticky="w", padx=(20, 4), pady=4
        )
        ttk.Label(perf_frame, textvariable=self.telemetry_vars["nn_duty"],
                  font=("TkDefaultFont", 11, "bold"), foreground="purple").grid(
            row=1, column=3, sticky="w", padx=4, pady=4
        )

        # Petunjuk interpretasi
        ttk.Label(perf_frame,
                  text="i Error positif = NN push duty naik | Error besar = saturasi (keterbatasan pompa)",
                  font=("TkDefaultFont", 9, "italic"), foreground="gray").grid(
            row=2, column=0, columnspan=4, sticky="w", padx=4, pady=(4, 0)
        )

        logging = ttk.LabelFrame(outer, text="CSV Logging", padding=10)
        logging.pack(fill="x", pady=10)
        ttk.Entry(logging, textvariable=self.csv_path_var).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ttk.Button(logging, text="Browse", command=self.choose_csv).grid(row=0, column=1, padx=4)
        self.log_button = ttk.Button(logging, text="Start Logging", command=self.toggle_logging)
        self.log_button.grid(row=0, column=2, padx=4)
        logging.columnconfigure(0, weight=1)

        log_frame = ttk.LabelFrame(outer, text="Serial Log", padding=10)
        log_frame.pack(fill="both", expand=True)
        self.log_text = tk.Text(log_frame, height=12, wrap="none")
        self.log_text.pack(fill="both", expand=True)

    def _sync_duty_label(self):
        self.set_duty_value(self.duty_var.get(), update_log=False)

    def set_duty_value(self, value, update_log=True):
        duty = max(0.0, min(95.0, round(float(value), 2)))
        self.duty_var.set(duty)
        self.duty_label.configure(text=f"{duty:.2f}")
        if update_log:
            self.append_log(f"# Duty set on GUI: {duty:.2f}%")

    def adjust_duty(self, delta):
        self.set_duty_value(self.duty_var.get() + delta)

    def set_valve_marker(self, value, phase, label=None):
        self.valve_open_count = str(value)
        self.valve_phase = phase
        if phase == "stable":
            display_value = label if label is not None else value
            self.valve_state_label = f"{display_value} keran stabil"
        elif phase == "transition_close":
            self.valve_state_label = "Transisi tutup cepat 4->0 keran"
        elif phase == "transition_open":
            self.valve_state_label = "Transisi buka cepat 0->4 keran"
        else:
            self.valve_state_label = "Transisi manual keran"
        self.valve_marker_var.set(f"Keran: {self.valve_state_label}")
        self.append_log(f"# Valve marker: {self.valve_state_label}")

    def reset_valve_marker(self):
        self.valve_open_count = "-"
        self.valve_state_label = "Belum ditandai"
        self.valve_phase = "unset"
        self.valve_marker_var.set("Keran: belum ditandai")
        self.append_log("# Valve marker reset")

    # === Auto Data Collection (closed-loop manual policy) ===
    def new_episode(self):
        """Mulai episode baru. Klik HANYA saat Anda me-reset/melompatkan duty
        ke nilai awal (memulai sesi kejar baru), bukan saat hanya ubah keran."""
        self.episode_id += 1
        self.episode_var.set(f"Episode: {self.episode_id}")
        self.append_log(f"# ===== Episode baru: {self.episode_id} =====")

    def set_event(self):
        """Stempel teks event ke kolom CSV (mis. 'gangguan 4->2', 'setpoint 0.35')."""
        self.event_marker = self.event_var.get().strip()
        self.append_log(f"# Event ditandai: '{self.event_marker}'")

    def clear_event(self):
        self.event_marker = ""
        self.event_var.set("")
        self.append_log("# Event dihapus")

    def toggle_auto_collect(self):
        if self.auto_collect_running:
            self.auto_collect_running = False
            if self._decision_after_id is not None:
                self.after_cancel(self._decision_after_id)
                self._decision_after_id = None
            self.auto_collect_button.configure(text="Start Auto-Collect")
            self.collect_status_var.set("Auto-collect: OFF")
            self.append_log("# Auto-collect dihentikan")
            return

        port = self.serial_worker.serial_port
        if port is None or not port.is_open:
            messagebox.showwarning("Belum connect", "Connect ke STM32 dulu sebelum auto-collect.")
            return
        if self.csv_writer is None:
            if not messagebox.askyesno(
                "Logging belum aktif",
                "CSV logging belum dimulai, jadi data keputusan TIDAK akan tersimpan.\n"
                "Lanjutkan auto-collect tanpa menyimpan?",
            ):
                return

        # Pastikan STM32 menurut perintah duty kita (open-loop), bukan NN
        self._send("SET,MODE,MANUAL")
        self.controller_mode.set("MANUAL")

        self.auto_collect_running = True
        self.auto_collect_button.configure(text="Stop Auto-Collect")
        self.collect_status_var.set("Auto-collect: ON")
        self.append_log(
            f"# Auto-collect MULAI | setpoint={self.collect_setpoint_var.get():.2f} bar "
            f"| interval={self.collect_interval_var.get():.1f}s | episode={self.episode_id}"
        )
        self._schedule_decision()

    def _schedule_decision(self):
        if not self.auto_collect_running:
            return
        interval_ms = max(500, int(self.collect_interval_var.get() * 1000))
        self._decision_after_id = self.after(interval_ms, self._decision_fire)

    def _decision_fire(self):
        if not self.auto_collect_running:
            return
        self._do_decision()
        self._schedule_decision()

    def _do_decision(self):
        if self.latest_row is None:
            self.append_log("# Auto-collect: belum ada telemetry, keputusan dilewati")
            return
        setpoint = self.collect_setpoint_var.get()
        pressure = self.latest_row["pressure_bar"]
        duty_now = self.duty_var.get()
        error = setpoint - pressure
        delta = policy_step(error)
        duty_min = self.collect_duty_min_var.get()
        new_duty = max(duty_min, min(COLLECT_DUTY_MAX, duty_now + delta))

        # Catat baris keputusan (state SEBELUM duty diubah) -> is_decision=1
        self._write_decision_row(setpoint, pressure, duty_now)

        # Terapkan duty baru
        self.set_duty_value(new_duty, update_log=False)
        self._send(f"SET,DUTY,{new_duty:.2f}")
        self.append_log(
            f"# [ep{self.episode_id} keran={self.valve_open_count}] "
            f"P={pressure:.3f} err={error:+.3f} duty {duty_now:.1f}->{new_duty:.1f} (d{delta:+d})"
        )

    def _write_decision_row(self, setpoint, pressure, duty_now):
        if self.csv_writer is None or self.latest_row is None:
            return
        row = dict(self.latest_row)
        row["pc_timestamp"] = datetime.now().isoformat(timespec="milliseconds")
        row["pressure_bar"] = pressure
        row["duty_percent"] = duty_now
        row["setpoint_bar"] = round(setpoint, 3)
        row["episode_id"] = self.episode_id
        row["is_decision"] = 1
        try:
            self.csv_writer.writerow([row[key] for key in CSV_HEADER])
            self.csv_file.flush()
        except OSError as exc:
            self.append_log(f"! CSV write error (decision): {exc}")

    def refresh_ports(self):
        ports = [port.device for port in list_ports.comports()]
        self.port_combo["values"] = ports
        if ports and not self.port_var.get():
            self.port_var.set(ports[0])

    def toggle_connection(self):
        if self.serial_worker.serial_port is not None and self.serial_worker.serial_port.is_open:
            if self.auto_collect_running:
                self.toggle_auto_collect()  # stop loop sebelum port ditutup
            self.serial_worker.disconnect()
            self.connect_button.configure(text="Connect")
            self.status_var.set("Disconnected")
            return
        port = self.port_var.get()
        if not port:
            messagebox.showwarning("Port kosong", "Pilih COM port STM32 terlebih dahulu.")
            return
        try:
            self.serial_worker.connect(port)
        except serial.SerialException as exc:
            messagebox.showerror("Serial error", str(exc))
            return
        self.connect_button.configure(text="Disconnect")
        self.status_var.set(f"Connected to {port}")

    def apply_duty(self):
        self._send(f"SET,DUTY,{self.duty_var.get():.2f}")

    def apply_frequency(self):
        self._send(f"SET,FREQ,{int(self.freq_var.get())}")

    def apply_both(self):
        self._send(f"SET,BOTH,{self.duty_var.get():.2f},{int(self.freq_var.get())}")

    def stop_pwm(self):
        self._send("STOP")

    def scan_jsy(self):
        self._send("SCANJSY")

    def apply_mode(self):
        """Baca radio button lalu kirim mode ke STM32"""
        mode = self.controller_mode.get()
        if mode == "MANUAL":
            self._send("SET,MODE,MANUAL")
            self.mode_status_label.configure(text="Status: MANUAL (open-loop)", foreground="blue")
            self.append_log("# Controller mode -> MANUAL (open-loop)")
        elif mode == "NN":
            self._send("SET,MODE,NN")
            self.mode_status_label.configure(text="Status: NN (closed-loop, auto)", foreground="green")
            self.append_log("# Controller mode -> NN (closed-loop, auto control)")
        else:
            self.append_log(f"# Mode tidak dikenal: {mode}")

    def query_mode(self):
        """Kirim GETMODE untuk cek mode saat ini di STM32"""
        self._send("GETMODE")

    def apply_setpoint(self):
        """Kirim SET,SETPOINT,<value> ke STM32"""
        sp = self.setpoint_var.get()
        # Validasi lokal (UI)
        if sp < 0.0:
            sp = 0.0
        if sp > 1.5:
            sp = 1.5
        self._send(f"SET,SETPOINT,{sp:.2f}")
        self.setpoint_status_var.set(f"(setpoint applied: {sp:.2f} bar)")
        self.append_log(f"# Setpoint applied: {sp:.2f} bar")

    def query_setpoint(self):
        """Kirim GETSETPOINT untuk cek setpoint saat ini"""
        self._send("GETSETPOINT")

    def _send(self, command):
        try:
            self.serial_worker.send(command)
        except RuntimeError as exc:
            messagebox.showwarning("Belum connect", str(exc))
            return
        self.append_log(f"> {command}")

    def choose_csv(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.csv_path_var.set(path)

    def toggle_logging(self):
        if self.csv_file is not None:
            self.csv_file.close()
            self.csv_file = None
            self.csv_writer = None
            self.log_button.configure(text="Start Logging")
            self.append_log("CSV logging stopped")
            return

        path = Path(self.csv_path_var.get())
        file_exists = path.exists() and path.stat().st_size > 0
        self.csv_file = path.open("a", newline="", encoding="utf-8")
        self.csv_writer = csv.writer(self.csv_file)
        self.last_csv_log_time = 0.0
        if not file_exists:
            self.csv_writer.writerow(CSV_HEADER)
            self.csv_file.flush()
        self.log_button.configure(text="Stop Logging")
        self.append_log(f"CSV logging started: {path}")

    def process_queue(self):
        while True:
            try:
                kind, payload = self.line_queue.get_nowait()
            except queue.Empty:
                break
            if kind == "ERROR":
                self.append_log(f"! {payload}")
                self.status_var.set("Serial error")
            else:
                self.handle_line(payload)
        self.after(50, self.process_queue)

    def handle_line(self, line):
        self.append_log(line)
        parts = line.split(",")
        if parts[0] == "DATA":
            if len(parts) not in (9, 16, 18, 20):
                return
        elif parts[0] == "MODE" and len(parts) == 3:
            # Response dari GETMODE: "MODE,NN,85.50"
            mode_str = parts[1].strip()
            try:
                nn_duty_val = float(parts[2])
            except ValueError:
                nn_duty_val = 0.0
            self.append_log(f"# Query Mode: STM32 mode = {mode_str}, NN output = {nn_duty_val:.2f}%")
            if self.controller_mode.get() != mode_str:
                self.controller_mode.set(mode_str)
            self.mode_status_label.configure(
                text=f"Status: {mode_str} (dari STM32)",
                foreground="green" if mode_str == "NN" else "blue"
            )
            return
        elif parts[0] == "SETPOINT" and len(parts) == 2:
            # Response dari GETSETPOINT: "SETPOINT,0.500"
            try:
                sp_val = float(parts[1])
                self.setpoint_var.set(sp_val)
                self.setpoint_status_var.set(f"(setpoint: {sp_val:.2f} bar)")
                self.append_log(f"# Query Setpoint: {sp_val:.2f} bar")
            except ValueError:
                pass
            return
        elif parts[0] == "MODE" and len(parts) == 4:
            # Extended response MODE,NN,85.50,0.500 (dengan setpoint)
            try:
                sp_val = float(parts[3])
                self.setpoint_var.set(sp_val)
                self.setpoint_status_var.set(f"(setpoint: {sp_val:.2f} bar)")
            except (ValueError, IndexError):
                pass
            return
        else:
            return
        try:
            has_float_payload = any("." in value for value in parts[3:9])
            if has_float_payload:
                adc_voltage = float(parts[3])
                sensor_voltage = float(parts[4])
                pressure_bar = float(parts[5])
                duty_percent = float(parts[6])
                estimated_rms = float(parts[8])
            else:
                adc_voltage = int(parts[3]) / 1000.0
                sensor_voltage = int(parts[4]) / 1000.0
                pressure_bar = int(parts[5]) / 1000.0
                duty_percent = int(parts[6]) / 100.0
                estimated_rms = int(parts[8]) / 100.0

            # Default nilai (untuk format 9-field tanpa JSY)
            nn_mode = 0
            nn_duty = 0.0

            row = {
                "pc_timestamp": datetime.now().isoformat(timespec="milliseconds"),
                "stm32_ms": int(parts[1]),
                "adc_raw": int(parts[2]),
                "adc_voltage_v": adc_voltage,
                "sensor_voltage_v": sensor_voltage,
                "pressure_bar": pressure_bar,
                "duty_percent": duty_percent,
                "frequency_hz": int(parts[7]),
                "estimated_output_rms_v": estimated_rms,
                "jsy_online": 0,
                "jsy_voltage_rms_v": 0.0,
                "jsy_current_rms_a": 0.0,
                "jsy_voltage_raw_v": 0.0,
                "jsy_current_raw_a": 0.0,
                "jsy_active_power_w": 0,
                "jsy_power_factor": 0.0,
                "jsy_energy_kwh": 0.0,
                "jsy_error_count": 0,
                "nn_mode": nn_mode,
                "nn_duty_percent": nn_duty,
                "valve_open_count": self.valve_open_count,
                "valve_state_label": self.valve_state_label,
                "valve_phase": self.valve_phase,
                "setpoint_bar": round(
                    self.collect_setpoint_var.get() if self.auto_collect_running
                    else self.setpoint_var.get(), 3),
                "episode_id": self.episode_id,
                "is_decision": 0,
                "event": self.event_marker,
            }
            if len(parts) == 16:
                row.update(
                    {
                        "jsy_online": int(parts[9]),
                        "jsy_voltage_rms_v": int(parts[10]) / 100.0,
                        "jsy_current_rms_a": int(parts[11]) / 1000.0,
                        "jsy_active_power_w": int(parts[12]),
                        "jsy_power_factor": int(parts[13]) / 1000.0,
                        "jsy_energy_kwh": int(parts[14]) / 1000.0,
                        "jsy_error_count": int(parts[15]),
                    }
                )
            elif len(parts) >= 18:
                # Format dengan nn_mode dan nn_duty (18 field),
                # plus opsional jsy_v_raw & jsy_i_raw di akhir (20 field).
                row.update(
                    {
                        "jsy_online": int(parts[9]),
                        "jsy_voltage_rms_v": int(parts[10]) / 100.0,
                        "jsy_current_rms_a": int(parts[11]) / 1000.0,
                        "jsy_active_power_w": int(parts[12]),
                        "jsy_power_factor": int(parts[13]) / 1000.0,
                        "jsy_energy_kwh": int(parts[14]) / 1000.0,
                        "jsy_error_count": int(parts[15]),
                        "nn_mode": int(parts[16]),
                        "nn_duty_percent": int(parts[17]) / 100.0,
                    }
                )
                if len(parts) >= 20:
                    # Nilai mentah JSY (sebelum kalibrasi) untuk telusur/re-kalibrasi
                    row["jsy_voltage_raw_v"] = int(parts[18]) / 100.0
                    row["jsy_current_raw_a"] = int(parts[19]) / 1000.0
                # Update mode display dari STM32 (hanya label, jangan ubah radio)
                # Catatan: radio button = pilihan user, telemetry = status STM32
                # Kita TIDAK overwrite radio button dari telemetry, agar klik user
                # tidak langsung "dilawan" oleh sinkronisasi otomatis.
                mode_str = "NN" if row["nn_mode"] == 1 else "MANUAL"
                if self.controller_mode.get() == mode_str:
                    # Sinkron -- update label warna
                    self.mode_status_label.configure(
                        text=f"Status: {mode_str} (sinkron)",
                        foreground="green" if mode_str == "NN" else "blue"
                    )
                else:
                    # Tidak sinkron -- mungkin STM32 belum update atau radio baru diklik
                    self.mode_status_label.configure(
                        text=f"Status STM32: {mode_str} (radio: {self.controller_mode.get()})",
                        foreground="red"
                    )

                # Update setpoint display dari telemetry (sinkron otomatis)
                # Note: setpoint di telemetry field 18 untuk 18-field format
                # Kita pakai local setpoint_var sebagai fallback
                if "setpoint_bar" in row:
                    sp_val = row["setpoint_bar"]
                else:
                    sp_val = self.setpoint_var.get()
                self.setpoint_display_var.set(f"{sp_val:.2f} bar")
            self.apply_sensor_moving_average(row)
        except ValueError:
            self.status_var.set("DATA parse error")
            return

        self.telemetry_vars["adc_raw"].set(str(row["adc_raw"]))
        self.telemetry_vars["adc_voltage"].set(f'{row["adc_voltage_v"]:.4f} V')
        self.telemetry_vars["sensor_voltage"].set(f'{row["sensor_voltage_v"]:.4f} V')
        self.telemetry_vars["pressure"].set(f'{row["pressure_bar"]:.3f} bar')
        self.telemetry_vars["duty"].set(f'{row["duty_percent"]:.2f} %')
        self.telemetry_vars["frequency"].set(f'{row["frequency_hz"]} Hz')
        self.telemetry_vars["rms"].set(f'{row["estimated_output_rms_v"]:.2f} Vrms')
        self.telemetry_vars["jsy_status"].set("Online" if row["jsy_online"] else "Offline")
        self.telemetry_vars["jsy_voltage"].set(f'{row["jsy_voltage_rms_v"]:.2f} Vrms')
        self.telemetry_vars["jsy_current"].set(f'{row["jsy_current_rms_a"]:.3f} Arms')
        self.telemetry_vars["jsy_power"].set(f'{row["jsy_active_power_w"]} W')
        self.telemetry_vars["jsy_pf"].set(f'{row["jsy_power_factor"]:.3f}')
        self.telemetry_vars["jsy_energy"].set(f'{row["jsy_energy_kwh"]:.3f} kWh')
        self.telemetry_vars["jsy_errors"].set(str(row["jsy_error_count"]))
        self.telemetry_vars["nn_duty"].set(f'{row["nn_duty_percent"]:.2f} %')

        # Hitung error display (setpoint - actual pressure)
        actual_pressure = row["pressure_bar"]
        sp_val = self.setpoint_var.get()
        error_val = sp_val - actual_pressure
        if abs(error_val) < 0.005:
            err_str = f"{error_val:+.3f} bar (TARGET tercapai)"
            err_color = "green"
        elif error_val > 0:
            err_str = f"{error_val:+.3f} bar (kurang dari target)"
            err_color = "red"
        else:
            err_str = f"{error_val:+.3f} bar (melebihi target)"
            err_color = "orange"
        self.error_display_var.set(err_str)
        # Update warna error label
        try:
            self.error_label_widget.configure(foreground=err_color)
        except AttributeError:
            pass  # Belum diinisialisasi

        # Simpan snapshot baris terakhir (dipakai loop keputusan auto-collect)
        self.latest_row = dict(row)

        now = time.monotonic()
        if self.csv_writer is not None and (now - self.last_csv_log_time) >= CSV_LOG_INTERVAL_SECONDS:
            try:
                self.csv_writer.writerow([row[key] for key in CSV_HEADER])
                self.csv_file.flush()
                self.last_csv_log_time = now
            except OSError as exc:
                self.append_log(f"! CSV write error: {exc}")
                self.status_var.set("CSV write error")

    def apply_sensor_moving_average(self, row):
        for key, buffer in self.sensor_average_buffers.items():
            buffer.append(row[key])
            row[key] = sum(buffer) / len(buffer)

    def append_log(self, line):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {line}\n")
        self.log_text.see("end")

    def destroy(self):
        self.auto_collect_running = False
        self.serial_worker.disconnect()
        if self.csv_file is not None:
            self.csv_file.close()
        super().destroy()


if __name__ == "__main__":
    App().mainloop()
