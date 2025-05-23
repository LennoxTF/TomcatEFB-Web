﻿import tkinter as tk
import math
import calc  

class CalcApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tomcat EFB")
        self.root.geometry("420x600")

        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Scrollable Canvas only for main menu
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.current_input = ""
        self.input_vars = []
        self.input_entries = []
        self.calc_func = None
        self.param_names = []

        # English + more intuitive labels
        self.functions = {
            "Navigation": {
                "groundspeed": (["Distance (NM)", "Time (h)"], "kt"),
                "time_to_dest": (["Distance (NM)", "Groundspeed (kt)"], "h"),
                "distance": (["Groundspeed (kt)", "Time (h)"], "NM"),
                "ETA": (["Distance (NM)", "Groundspeed (kt)"], "h"),
                "required_groundspeed_to_waypoint": (["Distance (NM)", "Current Time (HH:MM)", "TOT (HH:MM)"], "kt"),
            },
            "Climb / Descent": {
                "time_to_climb": (["Altitude Diff (ft)", "Climb Rate (ft/min)"], "min"),
                "climb_rate": (["Altitude Diff (ft)", "Time (min)"], "ft/min"),
                "top_of_descent": (["Altitude Diff (ft)", "Descent Gradient (°)"], "NM"),
                "descent_angle3": (["Groundspeed (kt)"], "°"),
                "descent_angle": (["Altitude Diff (ft)", "Distance (NM)"], "°"),
                "descent_rate_req": (["Altitude Diff (ft)", "Distance (NM)", "GS (kt)"], "ft/min"),
                "descent_profile": (["Altitude Diff (ft)", "GS (kt)", "Target Distance (NM)"], ""),
            },
            "Wind & Heading": {
                "WCA": (["TAS (kt)", "Wind Angle (°)", "Wind Speed (kt)"], "°"),
                "true_hdg": (["Track (°)", "WCA (°)"], "°"),
                "mag_hdg": (["True Heading (°)", "Magnetic Variation (°)"], "°"),
            },
            "Fuel & Range": {
                "fuel_per_nm": (["GS (kt)", "Fuel Flow (lb/h)"], "lb/NM"),
                "ranges": (["Fuel (lb)", "Fuel Rate (lb/h)", "GS (kt)"], "NM"),
                "fuel_at_fix": (["Current Fuel (lb)", "Speed (kt)", "Fuel Flow (lb/h)", "Distance (NM)"], "lb"),
            },
            "Temperature / ISA": {
                "isa_temperature": (["Altitude (ft)"], "°C"),
                "isa_deviation": (["Current Temp (°C)", "Altitude (ft)"], "°C"),
            }
        }

        self.show_main_menu()

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.current_input = ""
        self.input_vars.clear()
        self.input_entries.clear()

    def show_main_menu(self):
        self.clear_frame()

        # Scrollable content only here
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Synchronisiere Breite des Frames mit der Canvas-Breite
        def on_canvas_configure(event):
            self.canvas.itemconfig("frame", width=event.width)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n", tags="frame")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        self.canvas.bind("<Configure>", on_canvas_configure)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Zentrierte Inhalte im scrollbaren Frame
        title = tk.Label(self.scrollable_frame, text="Select a Calculation", font=("Arial", 14))
        title.pack(pady=10)

        for category, funcs in self.functions.items():
            cat_label = tk.Label(self.scrollable_frame, text=category, font=("Arial", 12, "bold"), fg="darkblue")
            cat_label.pack(pady=(10, 0))

            for func_name, (params, _) in funcs.items():
                label = func_name.replace("_", " ").capitalize()
                btn = tk.Button(self.scrollable_frame, text=label, width=35,
                                command=lambda f=func_name: self.show_input_screen(f))
                btn.pack(pady=2)

    def show_input_screen(self, func_name):
        self.clear_frame()

        for category in self.functions.values():
            if func_name in category:
                self.calc_func = getattr(calc, func_name)
                self.param_names = category[func_name][0]
                unit = category[func_name][1]
                break

        tk.Label(self.main_frame, text=f"Input: {func_name.replace('_', ' ').capitalize()}",
                 font=("Arial", 12)).pack(pady=10)

        for name in self.param_names:
            var = tk.StringVar()
            self.input_vars.append(var)
            frame = tk.Frame(self.main_frame)
            frame.pack(pady=4)
            tk.Label(frame, text=name + ":").pack(side="left")
            entry = tk.Entry(frame, textvariable=var, justify="right", font=("Arial", 12), width=10)
            entry.pack(side="right")
            entry.config(state="readonly")
            self.input_entries.append(entry)

        self.active_index = 0
        self.update_active_entry()
        self.create_numpad()

        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Calculate", command=self.calculate).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Back", command=self.show_main_menu).grid(row=0, column=1, padx=5)

        self.result_label = tk.Label(self.main_frame, text="", font=("Arial", 12), fg="blue")
        self.result_label.pack(pady=10)

    def update_active_entry(self):
        for i, entry in enumerate(self.input_entries):
            if i == self.active_index:
                entry.config(highlightthickness=2, highlightbackground="blue")
            else:
                entry.config(highlightthickness=0)

    def create_numpad(self):
        pad_frame = tk.Frame(self.main_frame)
        pad_frame.pack(pady=10)

        buttons = [
            ["7", "8", "9"],
            ["4", "5", "6"],
            ["1", "2", "3"],
            [".", "0", "Del"],
            ["<", ">"]
        ]

        for r, row in enumerate(buttons):
            for c, val in enumerate(row):
                btn = tk.Button(pad_frame, text=val, width=5, height=2,
                                command=lambda v=val: self.numpad_press(v))
                btn.grid(row=r, column=c, padx=2, pady=2)

    def numpad_press(self, value):
        var = self.input_vars[self.active_index]
        current = var.get()

        if value == "Del":
            var.set(current[:-1])
        elif value == "<":
            if self.active_index > 0:
                self.active_index -= 1
                self.update_active_entry()
        elif value == ">":
            if self.active_index < len(self.input_vars) - 1:
                self.active_index += 1
                self.update_active_entry()
        else:
            var.set(current + value)

    def calculate(self):
        try:
            values = []
            for v in self.input_vars:
                val = v.get()
                if ":" in val:
                    values.append(val)
                else:
                    values.append(float(val))

            result = self.calc_func(*values)

            if isinstance(result, dict):
                text = "\n".join([f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in result.items()])
                self.result_label.config(text=f"Result:\n{text}", fg="blue")
            elif result is None:
                self.result_label.config(text="Target time exceeded!", fg="red")
            else:
                unit = ""
                for category in self.functions.values():
                    if self.calc_func.__name__ in category:
                        unit = category[self.calc_func.__name__][1]
                        break
                self.result_label.config(text=f"Result: {round(result, 2)} {unit}", fg="blue")
        except Exception:
            self.result_label.config(text="Input error!", fg="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = CalcApp(root)
    root.mainloop()
