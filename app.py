from flask import Flask, render_template, jsonify
from sensor_utils import read_sensors
import threading
import I2C_LCD_driver
import RPi.GPIO as GPIO
from time import sleep

app = Flask(__name__)
lcd = I2C_LCD_driver.lcd()
sensor_data = {
    "temperature": 0,
    "humidity": 0,
    "light": "LOW",
    "rain": "DRY",
    "messages": [],
    "led_on": False,
    "alert_condition": False
}

def get_recommendations(temp, hum, light, rain):
    recs = []

    # Temperature rules
    if temp > 35:
        recs.append(("EXTREME HEAT!", "SHADE & WATER 2X"))
    elif temp > 30:
        recs.append(("HOT WEATHER", "WATER AT DAWN"))
    elif temp > 26:
        recs.append(("KEEP SOIL COVERED", "USING DRY LEAVES"))
    elif temp < 10:
        recs.append(("COLD RISK", "COVER BERRIES"))
    elif temp < 15:
        recs.append(("COOL WEATHER", "REDUCE WATERING"))

    # Humidity rules
    if hum > 85:
        recs.append(("HIGH HUMIDITY", "FUNGICIDE SPRAY"))
        recs.append(("MONSOON ALERT", "IMPROVE DRAINAGE"))
    elif hum > 75:
        recs.append(("HUMID", "TRIM BERRIES"))
    elif hum < 50:
        recs.append(("DRY SPELL", "WATER DEEPLY"))

    # Light and rain
    if light == "LOW" and rain == "WET":
        recs.append(("LOW LIGHT", "WATCH FOR MOLD"))
    elif light == "HIGH":
        recs.append(("STRONG SUN", "USE SHADE CLOTH"))

    # Default if no rules match
    if not recs:
        recs.append(("ALL NORMAL", "KEEP OBSERVING"))

    return recs

def update_lcd_and_data():
    global sensor_data
    while True:
        try:
            temp, hum, light, rain = read_sensors()
            
            if temp is None or hum is None:
                print("[WARNING] Sensor read failed, retrying...")
                sleep(2)
                continue
                
            recs = get_recommendations(temp, hum, light, rain)
            
            sensor_data.update({
                "temperature": round(temp),
                "humidity": round(hum),
                "light": light,
                "rain": rain,
                "messages": [f"{title}: {action}" for title, action in recs],
                "led_on": GPIO.input(17) == GPIO.HIGH,
                "alert_condition": (hum > 70 and temp > 20)
            })

            for title, action in recs:
                lcd.lcd_clear()
                lcd.lcd_display_string(title[:16], 1)
                lcd.lcd_display_string(action[:16], 2)
                sleep(3)
                
        except Exception as e:
            print(f"Error in sensor update: {e}")
            sleep(5)

@app.route('/')
def dashboard():
    return render_template("dashboard.html")

@app.route('/data')
def data():
    return jsonify(sensor_data)

if __name__ == '__main__':
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        thread = threading.Thread(target=update_lcd_and_data, daemon=True)
        thread.start()
        
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        lcd.lcd_clear()
        GPIO.cleanup()

