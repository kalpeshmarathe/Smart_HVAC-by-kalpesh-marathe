import tkinter as tk
from tkinter import ttk
import requests_cache
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from retry_requests import retry
import openmeteo_requests

requests_cache.install_cache('.cache', expire_after=3600)

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

class SmartHVACApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Smart HVAC Control by Kalpesh Marathe and Team")
        self.geometry("900x600")

        self.setpoint_temp = tk.DoubleVar(value=25.0)
        self.current_temp = tk.DoubleVar(value=25.0)
        self.num_people = tk.IntVar(value=1)
        self.room_diameter = tk.DoubleVar(value=1000.0)  
        self.ac_efficiency = tk.DoubleVar(value=0.5) 
        self.city = "Jalgaon"
        self.latitude = 21.0029
        self.longitude = 75.566


        self.create_widgets()

    
        self.time = []
        self.room_temps = []
        self.setpoint_temps = []

    def create_widgets(self):
  
        ttk.Label(self, text="Setpoint Temperature (°C):").pack(pady=5)
        ttk.Entry(self, textvariable=self.setpoint_temp).pack(pady=5)

        ttk.Label(self, text="Current Temperature (°C):").pack(pady=5)
        ttk.Entry(self, textvariable=self.current_temp, state='readonly').pack(pady=5)

        ttk.Label(self, text="Number of People:").pack(pady=5)
        ttk.Entry(self, textvariable=self.num_people).pack(pady=5)

        ttk.Label(self, text="Room Diameter (sqft):").pack(pady=5)
        ttk.Entry(self, textvariable=self.room_diameter).pack(pady=5)

        ttk.Label(self, text="AC Efficiency Factor:").pack(pady=5)
        ttk.Entry(self, textvariable=self.ac_efficiency).pack(pady=5)

  
        ttk.Button(self, text="Smart Control", command=self.start_control).pack(pady=10)


        self.plot_canvas = plt.figure(figsize=(6, 4))
        self.plot_ax = self.plot_canvas.add_subplot(111)
        self.plot_line, = self.plot_ax.plot([], [], 'b-', label='Room Temperature')
        self.plot_line_sp, = self.plot_ax.plot([], [], 'r--', label='Setpoint')
        self.plot_ax.legend()
        self.plot_ax.set_xlabel('Time')
        self.plot_ax.set_ylabel('Temperature (°C)')
        self.plot_canvas.tight_layout()
        self.plot_widget = FigureCanvasTkAgg(self.plot_canvas, master=self)
        self.plot_widget.get_tk_widget().pack(pady=10)

    def start_control(self):
        self.time = []
        self.room_temps = []
        self.setpoint_temps = []

        try:
            current_temp = self.get_current_temperature()
            self.current_temp.set(current_temp)
        except Exception as e:
            print("Error getting current temperature:", e)
            return

        # Adjust setpoint temperature based on room diameter and number of people
        room_area = self.room_diameter.get() / 10.764  # Convert sqft to sqm
        ac_capacity = room_area * self.num_people.get() * self.ac_efficiency.get()  # Adjust AC capacity based on room area and number of people
        desired_temp = self.current_temp.get() - ac_capacity * 0.1  # Adjust temperature based on AC capacity
        self.setpoint_temp.set(desired_temp)

        self.update_plot()

    def get_current_temperature(self):
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "hourly": "temperature_2m",
            "forecast_days": 1
        }
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        current_temp = hourly_temperature_2m[-1] 
        return current_temp

    def update_plot(self):
     
        time = np.arange(0, 10, 0.1)
        room_temps = np.random.normal(self.setpoint_temp.get(), 1, len(time))
        setpoint_temps = np.full_like(room_temps, self.setpoint_temp.get())

     
        self.time.extend(time)
        self.room_temps.extend(room_temps)
        self.setpoint_temps.extend(setpoint_temps)

        self.plot_line.set_data(self.time, self.room_temps)
        self.plot_line_sp.set_data(self.time, self.setpoint_temps)

        self.plot_ax.set_xlim(0, max(self.time))
        self.plot_ax.set_ylim(min(self.room_temps) - 1, max(self.room_temps) + 1)

        self.plot_widget.draw()

if __name__ == "__main__":
    app = SmartHVACApp()
    app.mainloop()
