<div align="center">

<img src="assets/braille/header.svg" width="100%" alt="Gabryel Lima written in braille dots under a Game of Life sky, a dead moon and a portal" />

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&pause=1200&color=FFD448&center=true&vCenter=true&width=560&lines=Hello!+I'm+Gabryel+Lima+%F0%9F%A4%96%F0%9F%90%8D;C11+%C2%B7+SDL2+%C2%B7+a+sky+written+in+braille+dots;Building+CharyRick+and+its+engine%2C+Grade;Linux+%C2%B7+Windows+%C2%B7+macOS+%C2%B7+Android+%C2%B7+EmuELEC" alt="Typing SVG" /></a>

<sub>Every dot above is computed by <a href="tools/braille_art.py"><code>tools/braille_art.py</code></a> with CharyRick's palette and 5×7 font — the sky is Conway's Game of Life, played forward and then rewound.</sub>

</div>

<div align="center"><img src="assets/braille/divider.svg" width="100%" alt="" /></div>

## 🎮 CharyRick

A **real-time co-op roguelike** (up to 4 players on one screen) written from scratch in **C11 + SDL2** and drawn
only with **braille dots and block pixels**. The sky pulses like Conway's Game of Life, something called the
Eraser is eating it, and you are a Reader going down to restore the Glyphs that hold it up.

<div align="center">
<img src="assets/charyrick/title.gif" width="640" alt="CharyRick title screen: the braille sky, the dead moon and the portal" /><br>
<sub><i>a co-op descent through a sky written in dots</i></sub>
</div>

<div align="center">
<table>
  <tr>
    <td align="center" width="50%"><img src="assets/charyrick/gameplay.gif" width="100%" alt="Two autopilot heroes clearing a sealed room" /><br><sub><b>Sealed rooms</b> · two heroes, waves of foes, “ROOM CLEARED”</sub></td>
    <td align="center" width="50%"><img src="assets/charyrick/boss.gif" width="100%" alt="The Warden boss fight" /><br><sub><b>The Warden</b> · first guardian, bullet rings</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="assets/charyrick/portal.gif" width="100%" alt="The portal unlocking with runes around the arch" /><br><sub><b>Portal unlock</b> · runes, the lock bursting, zoom</sub></td>
    <td align="center"><img src="assets/charyrick/blackhole.gif" width="100%" alt="Leaving the hub through a black hole" /><br><sub><b>Black hole</b> · leaving the hub</sub></td>
  </tr>
</table>
<sub>Recorded straight from the game with the autopilot (<code>--debug-record</code> piped into ffmpeg) — no editing.</sub>
</div>

### What I built inside it

<div align="center"><img src="assets/braille/orbit.svg" width="420" alt="A black hole with rings of braille dots turning" /></div>

| | |
|---|---|
| 🧩 **Grade** — my own engine library | braille canvas (each 2×4 block is a cell), pixel fonts with accents, sprites, field of view on a grid, composition layers with z-order, i18n that *fits the text in the box* (wrap → spill → scroll → pages, never shrinking the font) |
| 🔊 **Synth + sequencer** | every sound effect and the music are synthesized in code, no audio files; WAV export for videos |
| 🎲 **Deterministic simulation** | seeded floor generation (4×3 room grids), adaptive difficulty, an **autopilot bot** that plays whole runs — used for tests, balance reports and the GIFs above |
| 🌍 **One game, every platform** | Linux, Windows (MinGW cross-build), macOS (CI build), **Android** (NDK + touch controls with a layout editor) and **EmuELEC** (aarch64 TV console, built in Docker, tested in qemu) |
| 🧪 **Tooling** | CTest suites, headless captures compared byte by byte, a BM25 code search in pure Python, a C/assembly inspector, release packaging with debug tools compiled out |
| 🎬 **Videos** | gameplay, audio and frames exported on the same virtual clock, ready for explainer videos |

<sub>~60k lines of C · two languages (English / pt-BR) · Doxygen on every symbol</sub>

<div align="center"><img src="assets/braille/divider.svg" width="100%" alt="" /></div>

<div align="center">

## ⚙️ Where I live

<img src="https://skillicons.dev/icons?i=c,cpp,linux,bash,git,cmake,py" /><br><br>
<img src="https://img.shields.io/badge/SDL2-1b1f3a?style=for-the-badge&logo=c&logoColor=FFD448" />
<img src="https://img.shields.io/badge/Braille_rendering-1b1f3a?style=for-the-badge&logoColor=white" />
<img src="https://img.shields.io/badge/Game_engines-1b1f3a?style=for-the-badge&logoColor=white" />

## 🧰 Also in my toolbox

<img src="https://skillicons.dev/icons?i=cs,julia,go,lua,js,ts,react" /><br><br>
<img src="https://skillicons.dev/icons?i=ai,pytorch,tensorflow,sklearn,opencv,latex" /><br><br>
<img src="https://skillicons.dev/icons?i=docker,azure,mysql,vscode,github,powershell,discord" /><br>

## 📈 Studying now

<img src="https://skillicons.dev/icons?i=java,androidstudio,dart" /><br><br>
<img src="https://img.shields.io/badge/Android_NDK_%26_touch_input-3a265f?style=for-the-badge&logo=android&logoColor=54D4E8" />
<img src="https://img.shields.io/badge/ARM64_%2F_cross--compiling-3a265f?style=for-the-badge&logo=arm&logoColor=54D4E8" />
<img src="https://img.shields.io/badge/C_%E2%86%92_assembly-3a265f?style=for-the-badge&logoColor=white" />
<img src="https://img.shields.io/badge/Sound_synthesis-3a265f?style=for-the-badge&logoColor=white" />

<div align="center"><img src="assets/braille/divider.svg" width="100%" alt="" /></div>

[![GitHub Streak](https://streak-stats.demolab.com?user=Gabryel-lima&theme=dark&background=080A0C&ring=FFD448&fire=CE60DC&currStreakLabel=FFD448&sideLabels=54D4E8&dates=828C84&border=3A265F&border_radius=8)](https://git.io/streak-stats)

<a href="mailto:contatogabbryellimasi@gmail.com" target="_blank"><img src="https://img.shields.io/badge/Gmail-008000?style=for-the-badge&logo=gmail&logoColor=white"></a>
<a href="https://www.linkedin.com/in/gabryel-lima-9076541b2/" target="_blank"><img src="https://img.shields.io/badge/LinkedIn-1e90ff?style=for-the-badge&logo=linkedin&logoColor=white"></a>
<a href="https://www.youtube.com/@Code_Len" target="_blank"><img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white"></a>
<a href="https://open.spotify.com/artist/6d10RHPPNjPMUzyt3Tt99j?si=bu7NEga_Rbi8qF5D8D9bgA" target="_blank"><img src="https://img.shields.io/badge/Spotify-1DB954?style=for-the-badge&logo=spotify&logoColor=white"></a>

<br><br>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Gabryel-lima/Gabryel-lima/output/github-contribution-grid-snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Gabryel-lima/Gabryel-lima/output/github-contribution-grid-snake.svg" />
  <img alt="Snake eating my real contribution graph" src="https://raw.githubusercontent.com/Gabryel-lima/Gabryel-lima/output/github-contribution-grid-snake.svg" />
</picture>

</div>
