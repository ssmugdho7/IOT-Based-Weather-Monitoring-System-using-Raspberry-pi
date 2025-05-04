import Adafruit_DHT
import RPi.GPIO as GPIO
from smbus import SMBus
import time

# Sensor and GPIO Setup
DHT_PIN = 4
LDR_PIN = 27
PCF_ADDR = 0x48
DHT_SENSOR = Adafruit_DHT.DHT11
LED_PIN = 17
BUZZER_PIN = 18

# Musical note frequencies (Hz) - Full set including G3
C3 = 131; D3 = 147; E3 = 165; F3 = 175; G3 = 196; A3 = 220; B3 = 247
C4 = 261; D4 = 293; E4 = 329; F4 = 349; G4 = 392; A4 = 440; B4 = 493
C5 = 523

# Alert melodies and durations (ms)
CRITICAL_ALERT = {
    'melody': [E4, E4, E4, E4, E4, E4, E4, G4, C4, D4, E4, F4, F4, F4, F4],
    'durations': [200,200,200,200,200,200,200,200,200,200,200,200,200,200,200]
}

HIGH_HUMIDITY_ALERT = {
    'melody': [C4, G4, G4, A4, G4, 0, B4, C5],
    'durations': [400,200,200,400,400,400,400,400]
}

LOW_TEMP_ALERT = {
    'melody': [C4, D4, E4, F4, G4, A4, B4, C5],
    'durations': [300,300,300,300,300,300,300,300]
}

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(LDR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)
GPIO.output(BUZZER_PIN, GPIO.LOW)

def play_tone(pin, frequency, duration_ms):
    """Play a single tone with precise timing"""
    if frequency == 0:  # rest/pause
        time.sleep(duration_ms/1000.0)
        return
        
    period = 1.0 / frequency
    half_period = period / 2.0
    duration_s = duration_ms / 1000.0
    cycles = int(duration_s / period)
    
    for _ in range(cycles):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(half_period)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(half_period)

def play_melody(pin, melody_data):
    """Play a complete melody with LED feedback"""
    melody = melody_data['melody']
    durations = melody_data['durations']
    
    GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on LED during alert
    
    for i in range(len(melody)):
        play_tone(pin, melody[i], durations[i])
        time.sleep(0.03)  # short pause between notes
    
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.output(pin, GPIO.LOW)

def read_pcf8591(channel):
    """Read analog value from PCF8591"""
    bus = SMBus(1)
    try:
        bus.write_byte(PCF_ADDR, 0x40 | channel)
        bus.read_byte(PCF_ADDR)  # dummy read
        return bus.read_byte(PCF_ADDR)
    except Exception as e:
        print(f"[ERROR] PCF8591 read failed: {e}")
        return None
    finally:
        bus.close()

def read_sensors():
    """Read all sensors and trigger appropriate alerts"""
    hum, temp = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)
    
    # Default values if sensors fail
    if temp is None:
        temp = 0
        print("[WARNING] Failed to read temperature")
    if hum is None:
        hum = 0
        print("[WARNING] Failed to read humidity")
        
        
    if temp < 25 and temp > 15:  # Critical condition
        print("Optimal For Growth")   
    

    # Process alerts based on conditions
    if hum > 80 and temp > 28:  # Critical condition
        print("[ALERT] Critical: High temp and humidity!")
        play_melody(BUZZER_PIN, CRITICAL_ALERT)
    elif hum >85:  # High humidity
        print("[ALERT] High humidity detected")
        
    elif temp < 10:  # Low temperature
        print("[ALERT] Low temperature detected")
      
    else:
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(BUZZER_PIN, GPIO.LOW)

    # Read light sensor
    light_gpio = GPIO.input(LDR_PIN)
    light = "LOW" if light_gpio else "HIGH"

    # Read rain sensor
    rain_val = read_pcf8591(0)
    if rain_val is None:
        rain_val = 0
    rain = "WET" if rain_val < 50 else "DAMP" if rain_val < 150 else "DRY"

    print(f"[SENSOR] Temp: {temp}C, Hum: {hum}%, Light: {light}, Rain: {rain}")
    return temp, hum, light, rain

if __name__ == "__main__":
    try:
        print("Starting sensor monitoring...")
        while True:
            temp, hum, light, rain = read_sensors()
            time.sleep(2)  # Short delay between readings
            
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
    finally:
        GPIO.cleanup()
        print("GPIO cleanup complete")

