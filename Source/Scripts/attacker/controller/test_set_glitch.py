from controller.glitch_controller import GlitchController
import time

gps = GlitchController()

print("\nValori iniziali:")

print(gps.get_glitch())

choice = input(
    "Inserisci il valore del glitch x: "
).strip()

print("\nImposto glitch...")

gps.set_glitch(
    float(choice),
    0.0
)