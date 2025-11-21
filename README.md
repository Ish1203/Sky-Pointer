# 🌌 Sky Pointer – Gesture Controlled Mouse + Voice Assistant

Sky Pointer is a computer vision–based project that allows users to **control their computer cursor using hand gestures** and **operate their PC using voice commands** through the Luffy Voice Assistant.  
With the power of **OpenCV**, **MediaPipe**, **PyAutoGUI**, and AI-based voice automation, this project brings **touchless interaction** to desktop systems.

---

# 🚀 Screenshots

Real screenshots from the project:

| Cursor Move | Right Click | Brightness Control |
|------------|-------------|--------------------|
| ![](screenshot/Cursor%20Move.jpg) | ![](screenshot/Right%20Click.jpg) | ![](screenshot/Brightness%20Control.jpg) |

| Dual Hand Mode | Luffy Performing Tasks | Sky Pointer UI |
|----------------|------------------------|----------------|
| ![](screenshot/Dual%20Hand.jpg) | ![](screenshot/Luffy%20Performing%20multiple%20task.png) | ![](screenshot/Sky%20Pointer.jpg) |

---
# 🎯 Problem Statement

Traditional computer interaction depends heavily on devices like a mouse or touchpad.  
Sky Pointer provides a more **natural, accessible, and futuristic** way to interact using gestures and voice.

---

# 💡 Proposed Solution

- Capture real-time video using a webcam.  
- Detect hand landmarks using **MediaPipe Hands**.  
- Map index fingertip positions to **screen coordinates**.  
- Recognize gestures and perform:  
  - Mouse control  
  - Clicking  
  - Dragging  
  - Scrolling  
  - Volume & brightness adjustment  
  - Voice assistant activation  

---

# 🛠 Technologies Used

- **Python 3.9+**  
- **OpenCV**  
- **MediaPipe**  
- **NumPy**  
- **PyAutoGUI**  
- **PyCaw** (Volume control)  
- **Screen-Brightness-Control**  
- **Luffy Voice Assistant**  

---

# 📂 Project Structure

```
SkyPointer/
│
├── HandGesture.py           # Hand tracking & gesture detection
├── VirtualMouse.py          # Main logic for cursor and system controls
├── luffy/                   # Voice assistant module
├── screenshots/             # Screenshots for README
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```

---

# ✋ Gesture Control Guide

## 🖐️ Right Hand Controls (Primary Hand)

| Gesture | Pattern | Action |
|--------|---------|--------|
| 👉 **Move Cursor** | Index up | Move mouse |
| 🤏 **Left Click** | Index + Middle touching | Left click |
| 👍👉 **Right Click** | Thumb + Index up | Right click |
| ✊ **Drag Mode** | All fingers closed | Click & drag |
| ☝️ **Scroll Up** | Ring up | Scroll up |
| ✋ **Scroll Down** | Ring + Pinky up | Scroll down |
| 🤟 **Screenshot** | Thumb + Pinky up | Take screenshot |
| 🔁 **Switch Tab** | Thumb + Ring + Pinky | `Ctrl + Tab` |
| 💡 **Brightness** | Pinky up + thumb gap | Adjust brightness |
| 🫴 **Activate Luffy** | Index + Middle + Ring | Start voice assistant |

---

## ✋ Left Hand Controls (Secondary Hand)

| Gesture | Pattern | Action |
|--------|---------|--------|
| ✌️✌️ **Volume Control** | Index + Middle up | Volume up/down |
| 🖐️ **Minimize All** | All fingers up | `Win + D` |
| ✋🡅 **Maximize Window** | Index + Middle + Ring + Pinky up | `Win + Up` |
| 🤏✋ **Close Tab** | Thumb + Middle + Pinky | `Ctrl + W` |

---

# 🎙️ Luffy Voice Assistant Commands

## 1️⃣ Notes & Writing
| Command | Action |
|--------|--------|
| open notepad | Opens Notepad |
| write note | Creates notes.txt |
| read notes | Reads notes aloud |
| stop writing | Stop writing mode |

## 2️⃣ Apps & Websites
| Command | Action |
|--------|--------|
| open calculator | Launches Calculator |
| open command prompt | Opens CMD |
| open `<file>` | Opens file |
| open `<website>` | Open website |

## 3️⃣ Close Actions
| Command | Action |
|--------|--------|
| close notepad | Closes Notepad |
| close tab | Closes current tab |
| close it | Close last opened tab |

## 4️⃣ YouTube Controls
| Command | Action |
|--------|--------|
| play `<song>` on youtube | Plays a specific song |
| play `<playlist>` playlist | Plays playlist |
| next song / previous song | Controls playback |

## 5️⃣ Media Controls
- play / pause  
- volume up / volume down  
- mute  

## 6️⃣ System Commands
- shutdown  
- restart  
- lock  
- battery  
- time  
- date  

## 7️⃣ Windows & Tabs
- screenshot  
- change tab  
- minimize all  
- maximize window  

## 8️⃣ Weather
- weather / temperature  

---

# 🔮 Future Enhancements

- Custom hand gesture training  
- Multi-hand advanced actions  
- AR/VR gesture support  
- Voice assistant API integration  
- Gesture calibration UI  

---

# 🤝 Contributing

We welcome contributions!  
To contribute:

1. Fork this repository  
2. Create a new branch → `feature/your-feature`  
3. Commit your changes  
4. Push and open a Pull Request  

---

# ⭐ Support This Project

If you liked Sky Pointer, please **star ⭐ this repository** — it encourages us to build more futuristic projects!
