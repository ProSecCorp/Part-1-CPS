# First mid-term project: Cyber physical systems security
<p align="center">
  <img alt="Group logo, stylized images of a blue shield containing a bottle of prosecco, a drone, and connected chips" src="Data/Images/logo.jpeg" width="30%">
</p>
<h1 align="center">Professional Security Corporation</h1>
<p align="center">Project for the Course on
Cyber-Physical Systems and IoT Security (MSc ICT for Internet and Multimedia, A.Y. 2025/26) at University of Padua.</p>

## Members
- Emanuele Artusi | 2198545
- Filippo Bellon | XXXXXXX

## Reference paper
[Tractor Beam: Safe-hijacking of Consumer Drones with Adaptive GPS Spoofing](./Reference-paper.pdf)

## Setup
### LaTeX
To enable custom output paths and file naming via `latexmkrc`, the default LaTeX Workshop recipe must be replaced with a minimal one. Add the following entries to your VS Code `settings.json`:
```
"latex-workshop.latex.tools": [
  {
    "name": "latexmk-custom",
    "command": "latexmk",
    "args": ["-pdf", "%DOC%"]
  }
],

"latex-workshop.latex.recipes": [
  {
    "name": "latexmk (custom)",
    "tools": ["latexmk-custom"]
  }
]
```
Use **latexmk (custom)** when building the report.
This ensures LaTeX Workshop does not override `latexmkrc`, allowing the project’s custom output directory, jobname, and image paths to work as intended.
