# Harley-Davidson Charging System Diagnostics (Battery / Stator / Voltage Regulator-Rectifier) — Roadside / DIY Quick Guide

If you're stuck on the side of the road: read this top to bottom, in order. You'll need a basic multimeter.

### Step 1: Check the battery first
A weak or bad battery produces symptoms that look identical to a charging system failure. Always fully charge and load-test the battery FIRST before condemning the stator or regulator - otherwise all subsequent tests are unreliable.

### Step 2: Test the battery at rest
Standing/static battery voltage (engine off, fully charged, rested) should read approximately 12.5V to 13.2V DC. Readings meaningfully below 12.4V indicate the battery itself needs charging or may be failing.

### Step 3: Test the battery while the engine runs
With the engine running at roughly 2000-3000 RPM, DC voltage measured across the battery terminals should read approximately 13.0V to 14.7V (some sources tolerate up to 15V) if the charging system is healthy.

### Step 4: Low reading? It's probably the stator
If running voltage measures below ~13V, suspect the stator (charging system is undercharging).

### Step 5: High reading? It's probably the regulator
If running voltage exceeds ~15V, suspect the voltage regulator/rectifier (overcharging). Overcharging eventually damages ('cooks') the battery and can cause bulbs/electronics to fail.

### Step 6: Check your grounds before buying parts
Bad or corroded ground connections (battery-to-frame, regulator-to-frame) commonly mimic stator or regulator failure. Inspect and clean all ground connections before replacing any electrical component.

### Step 7: Test the stator directly
Stator AC output test: unplug the stator-to-regulator connector, set a multimeter to AC volts, start/rev the engine, and measure AC voltage across the stator pins. Typical output is roughly 16-26 VAC per 1000 RPM depending on the system's amp rating (varies by model/year - consult the factory service manual for exact spec). Never disconnect or reconnect the stator plug while the engine is running - it can destroy the stator.

### Step 8: Test the stator with the engine off
Stator resistance test: with the stator disconnected, resistance across the stator pins typically reads about 0.1-0.5 ohms depending on the system. A much higher reading or an open circuit indicates a broken winding (bad stator).

### Step 9: Make sure the stator isn't shorted
Stator ground test: with the stator disconnected, there should be NO continuity between any stator pin and the frame/engine ground. Continuity to ground means the stator is shorted (bad).

### Step 10: Test the regulator directly
Voltage regulator bleed-back test: with the regulator unplugged from the stator (battery still connected), probe the regulator's output-side pins with a test light or voltmeter referenced to battery negative. Any voltage or illumination means the regulator is bad ('leaking' voltage).
