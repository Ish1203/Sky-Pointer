# 🌌 Sky Pointer – Gesture Controlled Pointer  

Sky Pointer is a computer vision project that allows users to **control the cursor using hand gestures** instead of a physical mouse.  
It uses **OpenCV**, **MediaPipe**, and **PyAutoGUI** to detect hand movements via a webcam and translate them into system cursor actions.  

---

## 🎯 Problem Statement  

Traditional computer interaction relies heavily on physical input devices like a mouse or touchpad.  
This project explores a more **natural and touchless interaction method** using **hand gestures** for pointer control.

---

## 💡 Proposed Solution  

- Use a **webcam** to capture real-time video.  
- Detect **hand landmarks** using **MediaPipe Hands**.  
- Map finger movements to **screen coordinates** with OpenCV.  
- Simulate cursor actions (move, click, drag, scroll, volume/brightness control) using PyAutoGUI & Pycaw.  

---

## 🛠️ Tools & Technologies  

- **Python 3.x**  
- **OpenCV** – For video capture & image processing  
- **MediaPipe** – For real-time hand tracking & gesture recognition  
- **NumPy** – For calculations and transformations  
- **PyAutoGUI** – For controlling mouse cursor and actions  
- **PyCaw** – For controlling system audio (optional)  
- **Screen Brightness Control** – For brightness adjustments (optional)  

---

## 📂 Project Structure  

```bash
SkyPointer/
│
├── HandGesture.py         # Core hand tracking & gesture recognition
├── VirtualMouse.py        # Main file for controlling cursor via webcam
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation



🎮 How It Works

✋ Hand Detection – Place your hand in front of the webcam.

👉 Index Finger – Cursor movement.

👌 Index + Thumb pinch – Left click.

🖐 Two fingers up – Right click.

✊ Closed fist – Drag.

☝️ Volume/Brightness gestures – Control system volume or brightness.

(Gestures may vary depending on implementation.)


🌱 Future Enhancements

🔐 Add custom gesture recognition.

🎯 Improve accuracy with smoothing filters.

🖥 Multi-hand control for more functionality.

📱 Extend support for touchless interactions in AR/VR environments.



🤝 Contributing

Contributions are welcome! To contribute:

Fork the repository

Create a new branch (feature/your-feature-name)

Commit your changes

Push to your fork and open a Pull Request


# Please star our repo for support
