from glitch_controller import GlitchController
import time

gps = GlitchController()

print("\nValori iniziali:")

print(gps.get_glitch())

print("\nImposto glitch...")

gps.set_glitch(
    0.00002,
    -0.00001
)

time.sleep(1)

print(gps.get_glitch())

print("\nReset")

gps.reset()

time.sleep(1)

print(gps.get_glitch())