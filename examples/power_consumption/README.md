This code is based on the PR https://github.com/microsoft/AirSim/pull/3242

To use it, you must first open the Unreal environment and start the simulation (pressing the Start button on Unreal).
So, before arming the drone, execute the `power_consumption.py`, which will begin to count the **Instantaneous Power (`Pi`)** and Total **Power Consumption (`Pt`)**.

Therefore, while the rotors turn, the total power consumed will increase. That's why executing the code before the rotors start working is essential to get total consumed power from the beginning of the mission.

When the mission is finished, just stop the code execution and save the last value of `Pt`.