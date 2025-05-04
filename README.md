# IOT-Based-Weather-Monitoring-System-using-Raspberry-pi


As we know, strawberries are delicate crops that require very specific environmental conditions to grow properly—particularly in terms of temperature, humidity, light, and moisture. Even a slight shift in weather can lead to poor yield, fungal diseases, or plant stress. That's where our solution comes in.

Our system uses a Raspberry Pi connected to multiple sensors including:

A DHT11 for temperature and humidity,
An LDR for ambient light,
A rain sensor via a PCF8591 ADC module.

These sensors collect real-time environmental data, which is then processed to identify any critical conditions. When conditions such as extreme heat, high humidity, or low temperature are detected, the system automatically triggers alerts—a buzzer sounds a melody, and an LED lights up, notifying farmers instantly.

We’ve also built a Flask-based web dashboard that displays the live data from all sensors, along with AI-driven recommendations. These recommendations include actions like:

Watering strategies during heatwaves,
Using fungicide during high humidity,
Providing shade in strong sunlight.

To ensure local usability, we integrated an I2C-based LCD display, which cycles through real-time tips and warnings even without internet access—making the system suitable for rural settings.

The AI part of the system lies in the rule-based recommendation engine. Based on temperature, humidity, and other factors, the engine intelligently advises the best agricultural practices to protect strawberry crops.
