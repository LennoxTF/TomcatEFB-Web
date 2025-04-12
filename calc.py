# -*- coding: utf-8 -*-
import math
from datetime import datetime

def groundspeed(dist, time):
    # dist in NM, time in h → speed in kt (NM/h)
    groundspeed = dist / time
    return f"{groundspeed:.1f} kt"

def time_to_dest(dist, speed):
    # dist in NM, speed in kt → time in h
    time = dist / speed
    return f"{time:.1f} h"

def distance(speed, time):
    # speed in kt, time in h → distance in NM
    distance = speed * time
    return f"{distance:.1f} NM"

def WCA(tas, angle, windspeed):
    # tas in kt, windspeed in kt, angle in degrees (between wind dir and desired track)
    angle_rad = math.radians(angle)
    ratio = (windspeed * math.sin(angle_rad)) / tas
    # Clamp ratio to valid range for asin
    ratio = max(min(ratio, 1), -1)
    wca_rad = math.asin(ratio)
    wca_deg = math.degrees(wca_rad)
    return f"{wca_deg:.1f} deg"

def true_hdg(track, wca):
    # track and wca in degrees → result in degrees
    true_hdg = track + wca
    return f"{true_hdg:.1f} deg"

def mag_hdg(true_hdg, declination):
    # true_hdg and declination in degrees
    mag_hdg = true_hdg - declination
    return f"{mag_hdg:.1f} deg"

def fuel_per_nm(speed, fuel_rate):
    # speed in kt (NM/h), fuel_rate in lbs/h → result in lbs/NM
    fuel_per_nm = fuel_rate / speed
    return f"{fuel_per_nm:.1f} lbs/NM"

def ranges(fuel, fuel_rate, speed):
    # fuel in lbs, fuel_rate in lbs/h, speed in kt → result in NM
    ranges = (fuel / fuel_rate) * speed
    return f"{ranges:.1f} NM"

def time_to_climb(altitude, rate_of_climb):
    # altitude in ft, rate_of_climb in ft/min → result in minutes
    time_to_climb = altitude / rate_of_climb
    return f"{time_to_climb:.1f} min"

def climb_rate(altitude, time):
    # altitude in ft, time in min → result in ft/min
    rate_of_climb = altitude / time
    return f"{rate_of_climb:.1f} ft/min"

def ETA(distance, speed):
    # distance in NM, speed in kt → result in h
    eta = distance / speed
    return f"{eta:.1f} h"

def top_of_descent(altitude, nm_per_1000ft):
    # altitude in ft, nm_per_1000ft typical value = 3 for 3° path
    tod = (altitude / 1000) * nm_per_1000ft
    return f"{tod:.1f} NM"

def descent_angle3(speed):
    # Placeholder – real descent angle depends on geometry, not just speed
    # Here we return the commonly used formula for a 3° glide path:
    descent_angle = 3  # degrees – standard approach angle
    return f"{descent_angle:.1f} deg"

def descent_angle(altitude, distance):
    # altitude in ft, distance in NM → convert NM to ft
    distance_ft = distance * 6076.12
    descent_angle_rad = math.atan(altitude / distance_ft)
    descent_angle_deg = math.degrees(descent_angle_rad)
    return f"{descent_angle3:.1f} deg"

def descent_rate_req(altitude, distance, speed):
    # altitude in ft, distance in NM, speed in kt (NM/h)
    # Convert speed to NM/min: kt / 60
    # descent_rate in ft/min
    nm_per_min = speed / 60
    descent_rate = (altitude / distance) * nm_per_min
    return f"{descent_rate:.1f} NM/h"

def isa_temperature(altitude):
    # altitude in ft → ISA Temp in °C
    return f"{15 - (altitude / 1000 * 2):.1f} deg C"

def isa_deviation(actual_temp, altitude):
    return f"{actual_temp - isa_temperature(altitude)}:.1f} deg C"

def fuel_at_fix(current_fuel, speed, fuel_rate, distance):
    # Treibstoff nach Flug zum Fix (alles in kt, lbs/h, NM)
    time = distance / speed  # h
    fuel_used = fuel_rate * time
    return f"{current_fuel - fuel_used:.1f} lbs"

def required_groundspeed_to_waypoint(distance_nm, current_time_str, target_time_str):
    """
    Berechnet die erforderliche Geschwindigkeit in Knoten (KTAS), 
    um zu einem Waypoint genau zur Zielzeit (TOT) anzukommen.

    :param distance_nm: Entfernung zum Waypoint (NM)
    :param current_time_str: aktuelle Zeit (z. B. "14:23")
    :param target_time_str: Zielzeit am Waypoint (z. B. "14:30")
    :return: benötigte Geschwindigkeit in KT oder None, wenn TOT nicht erreichbar
    """
    fmt = "%H:%M"
    current_time = datetime.strptime(current_time_str, fmt)
    target_time = datetime.strptime(target_time_str, fmt)

    delta_seconds = (target_time - current_time).total_seconds()

    if delta_seconds <= 0:
        return None  # TOT in der Vergangenheit

    time_hours = delta_seconds / 3600
    required_speed = distance_nm / time_hours
    return f"{required_speed:.1f} kt"

def descent_profile(altitude_ft, ground_speed_kt, target_distance_nm):
    """
    Berechnet ein vollständiges Sinkflugprofil basierend auf Flughöhe, GS und Zielentfernung.
    Gibt Descent Angle, Sinkrate und idealen Sinkpunkt aus.
    """
    # In Stunden umrechnen
    time_hours = target_distance_nm / ground_speed_kt
    time_minutes = time_hours * 60

    # Sinkrate
    sink_rate_fpm = altitude_ft / time_minutes

    # Descent angle (in Grad)
    descent_angle_deg = math.degrees(math.atan(altitude_ft / (target_distance_nm * 6076.12)))  # ft vs ft

    return {
        "sink_rate_fpm": round(sink_rate_fpm, 1),
        "descent_angle_deg": round(descent_angle_deg, 2),
        "top_of_descent_nm": round(target_distance_nm, 2),
        "time_to_descent_min": round(time_minutes, 1)
    }

def endurance(fuel_lb, fuel_flow_lb_per_hour):
    """
    Calculate endurance (how long you can fly) based on remaining fuel and fuel flow.

    Parameters:
        fuel_lb (float): Remaining fuel in pounds.
        fuel_flow_lb_per_hour (float): Fuel consumption in lb/h.

    Returns:
        str: Endurance in the format "Xh Ymin".
    """
    if fuel_flow_lb_per_hour <= 0:
        raise ValueError("Fuel flow must be greater than 0.")
        
    endurance_hours = fuel_lb / fuel_flow_lb_per_hour
    hours = int(endurance_hours)
    minutes = int((endurance_hours - hours) * 60)

    return f"{hours}h {minutes}min"
