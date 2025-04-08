import tkinter as tk
from tkinter import ttk
import math
import calc

class CalcApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tomcat EFB")
        self.root.geometry("420x600")
        self.root.configure(bg="#223")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=6, relief="flat", background="#345", foreground="white")
        style.map("TButton",
                  background=[("active", "#456")],
                  relief=[("pressed", "sunken")])

        self.scroll_canvas_frame = tk.Frame(root, bg="#223")
        self.canvas = tk.Canvas(self.scroll_canvas_frame, bg="#223")
        self.scrollbar = ttk.Scrollbar(self.scroll_canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#223")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas_frame.pack(fill="both", expand=True)

        self.flat_frame = tk.Frame(root, bg="#223")

        self.current_input = ""
        self.input_vars = []
        self.input_entries = []
        self.calc_func = None
        self.param_names = []

        self.functions = {
            "Navigation": {
                "groundspeed": (["Distance (nm)", "Time (h)"], "kt"),
                "time_to_dest": (["Distance (nm)", "Groundspeed (kt)"], "h"),
                "distance": (["Groundspeed (kt)", "Time (h)"], "nm"),
                "ETA": (["Distance (nm)", "Groundspeed (kt)"], "h"),
                "required_groundspeed_to_waypoint": (["Distance (nm)", "Current Time (HH:MM)", "TOT (HH:MM)"], "kt"),
            },
            "Climb / Descent": {
                "time_to_climb": (["Altitude Diff (ft)", "Climb Rate (ft/min)"], "min"),
                "climb_rate": (["Altitude Diff (ft)", "Time (min)"], "ft/min"),
                "top_of_descent": (["Altitude Diff (ft)", "Gradient (e.g. 3)"], "nm"),
                #"descent_angle3": (["Groundspeed (kt)"], "°"),
                "descent_angle": (["Altitude Diff (ft)", "Distance (nm)"], "°"),
                "descent_rate_req": (["Altitude Diff (ft)", "Distance (nm)", "GS (kt)"], "ft/min"),
                "descent_profile": (["Altitude Diff (ft)", "GS (kt)", "Target Distance (nm)"], ""),
            },
            "Wind & Heading": {
                "WCA": (["TAS (kt)", "Wind Angle (°)", "Wind Speed (kt)"], "°"),
                "true_hdg": (["Track (°)", "WCA (°)"], "°"),
                "mag_hdg": (["True Heading (°)", "Mag. Deviation (°)"], "°"),
            },
            "Fuel & Range": {
                "fuel_per_nm": (["GS (kt)", "Fuel Flow (lb/h)"], "lb/nm"),
                "ranges": (["Fuel (lb)", "Fuel Rate (lb/h)", "GS (kt)"], "nm"),
                "fuel_at_fix": (["Current Fuel (lb)", "Speed (kt)", "Fuel Flow (lb/h)", "Distance (nm)"], "lb"),
                "endurance": (["Fuel (lb)", "Fuel Flow (lb/h)"], "h"),
            },
            "Temperature / ISA": {
                "isa_temperature": (["Altitude (ft)"], "°C"),
                "isa_deviation": (["Current Temp (°C)", "Altitude (ft)"], "°C"),
            }
        }

        self.show_main_menu()
        self.bind_scroll_events()

    def bind_scroll_events(self):
        # Windows + Linux
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        # macOS
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))


    def clear_frame(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        for widget in self.flat_frame.winfo_children():
            widget.destroy()
        self.current_input = ""
        self.input_vars.clear()
        self.input_entries.clear()

    def show_main_menu(self):
        self.flat_frame.pack_forget()
        self.scroll_canvas_frame.pack(fill="both", expand=True)

        self.clear_frame()
        title = tk.Label(self.scrollable_frame, text="Select a Calculation", font=("Segoe UI", 16, "bold"), bg="#223", fg="white")
        title.pack(pady=10)

        for category, funcs in self.functions.items():
            cat_frame = tk.LabelFrame(self.scrollable_frame, text=category, font=("Segoe UI", 12, "bold"),
                                      bg="#112", fg="lightblue", padx=10, pady=10, labelanchor="n")
            cat_frame.pack(pady=8, padx=20, fill="x")

            for func_name, (params, _) in funcs.items():
                label = func_name.replace("_", " ").capitalize()
                btn = ttk.Button(cat_frame, text=label, width=30,
                                 command=lambda f=func_name: self.show_input_screen(f))
                btn.pack(pady=4)

    def show_input_screen(self, func_name):
        self.scroll_canvas_frame.pack_forget()
        self.flat_frame.pack(fill="both", expand=True)

        self.clear_frame()

        for category in self.functions.values():
            if func_name in category:
                self.calc_func = getattr(calc, func_name)
                self.param_names = category[func_name][0]
                unit = category[func_name][1]
                break

        tk.Label(self.flat_frame, text=f"Input: {func_name.replace('_', ' ').capitalize()}",
                 font=("Segoe UI", 14), bg="#223", fg="white").pack(pady=10)

        for name in self.param_names:
            var = tk.StringVar()
            self.input_vars.append(var)
            frame = tk.Frame(self.flat_frame, bg="#223")
            frame.pack(pady=4)
            tk.Label(frame, text=name + ":", bg="#223", fg="white", font=("Segoe UI", 11)).pack(side="left")
            entry = tk.Entry(frame, textvariable=var, justify="right", font=("Segoe UI", 12), width=10)
            entry.pack(side="right")
            entry.config(state="readonly")
            self.input_entries.append(entry)

        self.active_index = 0
        self.update_active_entry()

        self.create_numpad()

        btn_frame = tk.Frame(self.flat_frame, bg="#223")
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Calculate", command=self.calculate).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Back", command=self.show_main_menu).grid(row=0, column=1, padx=5)

        self.result_label = tk.Label(self.flat_frame, text="", font=("Segoe UI", 12), fg="lightblue", bg="#223")
        self.result_label.pack(pady=10)

    def update_active_entry(self):
        for i, entry in enumerate(self.input_entries):
            if i == self.active_index:
                entry.config(highlightthickness=2, highlightbackground="lightblue")
            else:
                entry.config(highlightthickness=0)

    def create_numpad(self):
        pad_frame = tk.Frame(self.flat_frame, bg="#223")
        pad_frame.pack(pady=10)

        buttons = [
            ["7", "8", "9"],
            ["4", "5", "6"],
            ["1", "2", "3"],
            [".", "0", "Del"],
            [":", "<", ">"]
        ]

        for r, row in enumerate(buttons):
            for c, val in enumerate(row):
                btn = ttk.Button(pad_frame, text=val, width=5,
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
                self.result_label.config(text=f"Result:\n{text}", fg="lightblue")
            elif result is None:
                self.result_label.config(text="Target time exceeded!", fg="red")
            else:
                unit = ""
                for category in self.functions.values():
                    if self.calc_func.__name__ in category:
                        unit = category[self.calc_func.__name__][1]
                        break

                if isinstance(result, str):
                    self.result_label.config(text=f"Result: {result}", fg="lightblue")
                else:
                    self.result_label.config(text=f"Result: {round(result, 2)} {unit}", fg="lightblue")

        except Exception:
            self.result_label.config(text="Input error!", fg="red")


if __name__ == "__main__":
    root = tk.Tk()
    app = CalcApp(root)
    root.mainloop()
