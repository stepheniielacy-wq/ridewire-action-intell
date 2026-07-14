# Harley-Davidson Ignition & Starting System Diagnostics (No-Crank / No-Start Troubleshooting) — Roadside / DIY Quick Guide

If you're stuck on the side of the road: read this top to bottom, in order. You'll need a basic multimeter.

### Step 1: Check your battery voltage first
For reliable starter engagement, resting battery voltage should read at least approximately 12.4-12.6V DC. Below that, the battery may still register a voltage reading but lack enough cold-cranking amperage to spin the starter, producing symptoms - a single click, no crank, or slow crank - that closely mimic relay or solenoid failure.

### Step 2: Make sure you can actually start it (clutch, neutral, side stand)
Most Harley-Davidson models require specific switch states before the starter circuit will engage, typically the clutch lever pulled in (via a microswitch in the clutch perch) combined with the transmission in neutral or the clutch held in - exact logic varies by year/model, so consult the model-specific wiring diagram. Many models also use a side-stand ('jiffy stand') interlock that can prevent starting or cut ignition if the stand is down while the transmission is in gear. A failed or misaligned clutch-perch microswitch is a common, overlooked cause of a bike that 'won't start' despite good battery, starter, and relay.

### Step 3: Listen to what it does when you press start
A single loud click (or repeated clicking) when pressing the start button, without the engine cranking, most commonly indicates either (a) insufficient battery amperage to hold the solenoid closed under load even with adequate resting voltage, (b) a solenoid or starter with worn contacts / high internal resistance, or (c) a bad ground or connection somewhere between the battery, solenoid, and starter. Clicking alone does not necessarily mean the starter motor itself is bad.

### Step 4: Load-test the battery while cranking
Voltage-drop / cranking load test: with the battery fully charged and the engine disabled from firing (ignition disabled or plugs pulled), crank the starter for a few seconds while monitoring battery voltage with a multimeter. A healthy system shows only a small, consistent drop across each cable and connection rather than a large drop at any single point; as a rule of thumb, voltage should not fall below roughly 9.6-10V during cranking, and a drop into the 7-9V range signals a weak or failing battery rather than a starter/relay fault.

### Step 5: Know your starter relay terminals
Harley-Davidson starter relays on most Evolution/Twin Cam/Milwaukee-Eight era models use the industry-standard DIN 72552 4-pin relay layout: terminal 30 = constant/switched battery positive (common), terminal 87 = output to the starter solenoid, terminal 86 = trigger signal from the start button/switch, terminal 85 = ground for the relay coil. Older Ironhead/Shovelhead-era relays can use a different, non-DIN 3-terminal numbering - always confirm against the specific model's wiring diagram before testing.

### Step 6: Test the starter relay
To test whether a suspect starter relay itself is the point of failure, pull the relay from its socket and use a jumper wire to bridge terminals 30 and 87 directly (bypassing the relay's coil/switch path entirely) with the ignition on and the transmission in neutral. If the starter now cranks, the relay itself is bad; if it still doesn't crank, the fault lies elsewhere (wiring, solenoid, starter, battery, or ground) and the relay should not be replaced on this evidence alone.

### Step 7: Test the starter solenoid directly
To isolate whether the starter solenoid or the wiring/relay upstream of it is at fault, apply 12V directly from the battery positive terminal to the solenoid's small trigger terminal (bypassing the relay and start button entirely). If the starter engages and cranks, the relay/wiring/switch side is at fault, not the solenoid or starter; if it still doesn't crank, suspect the solenoid, starter, or the battery-to-starter power/ground path itself.

### Step 8: Check for a security-module fault
Many Harley-Davidson models built roughly 2001-2013 have a Turn Signal/Security Module (TSM/TSSM), and later CAN-bus models use similar security modules (e.g. HFSM), that can log ignition-enable and starter-related fault codes and, in some fault states, restrict the starter circuit as an anti-theft measure. A common false alarm is a dying key fob battery or a blown turn-signal bulb triggering a security light or trouble code without any actual starter hardware fault - rule these out before condemning the relay, solenoid, or starter on models with this system.

### Step 9: Reset the security module
Standard TSM/TSSM code-check and reset procedure (non-CAN-bus models, roughly 2001+): with the ignition switch OFF and the Run/Stop switch in RUN, press and hold the odometer reset button while turning the ignition switch to ON; release the button once the dash sweeps and 'DIAG' appears; step through the 'PSSPT' selection menu using the reset button to reach the security ('S') code check; press and hold the reset button to display any stored code, or 'NONE' if there isn't one; hold again while the code is displayed to clear it until 'CLEARED' appears. Exact menu steps and the 5-digit fault code list vary slightly by model year - always check for a dying key fob battery first, since that is a frequent false trigger.

### Step 10: Still stuck? Work through the full order
When a Harley won't crank at all (including no click and no sound), diagnose in this order rather than jumping to parts replacement: (1) battery voltage and condition first - a resting battery below roughly 12.4V may show voltage but lack enough amperage to spin the starter, (2) battery terminal and ground connections for corrosion or looseness, (3) starter relay, (4) starter solenoid, (5) starter motor itself, (6) safety interlock switches (clutch/neutral/side-stand) and their wiring. Skipping ahead to component replacement before checking connections and battery condition is the most common cause of misdiagnosis.
