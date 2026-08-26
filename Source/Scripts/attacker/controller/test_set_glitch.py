from controller.glitch_controller import GlitchController
import time

gps = GlitchController()

print("\nInitial values:")

print(gps.get_glitch())

choice = input(
    "Enter the x value for the glitch: "
).strip()

print("\nSetting glitch...")

gps.set_glitch(
    float(choice),
    0.0
)