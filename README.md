<h1 align=left>
  <b>OBS Playing now Overlay</b>
  <br>
  <sup><sub>Powered by MPRIS and HTML/CSS/JS</sub></sup>
</h1>

This script allows you to show what you're listening to using the OBS Browser Source<br>
Currently only Linux is supported, and there are no plans to make this work with Windows

## Installation and Usage
Unfortunately this can't be built with pyinstaller or the likes

**Dependencies**

Arch Linux:
```
pacman -S --needed python3 python-flask python-jeepney python-asgiref
```
Debian:
```
apt install python3 python3-flask python3-jeepney python3-asgiref
```
PIP (Not recommended)
```
pip install flask flask[async] jeepney
```

1. Clone the repository
2. Go to Tools > Scripts in OBS Studio
3. Add ``start_overlay.py`` as a script
4. Change the port if needed, and select your player from the list
5. Add a browser source
6. Set the URL as ``127.0.0.1:<port>`` (Default port is 5000)
7. Check ``Shutdown source when not visible`` and ``Refresh browser when scene becomes active``
8. Done!

(Optional) Width 800 and Height 225 are ideal

## Customization
The overlay itself is just HTML, CSS and JavaScript so it should be easy to modify as you wish<br>
Maybe I'll make more themes someday...

## Screenshots
<img width="600" alt="Screenshot 2026-10-24 09-38-44" src="https://github.com/user-attachments/assets/c3e51648-1895-4887-b2f1-14318a512b36" />
