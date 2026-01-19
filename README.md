# Gesture-Controlled Pong

A simple computer vision Pong game using OpenCV and MediaPipe.  
The game is controlled entirely with hand gestures using a webcam.

## Features

- Hand-tracked paddle control
- Fist gesture to start and stop the game
- On-screen START button
- Countdown before gameplay begins
- Two-player support using both hands
- Angle-based ball physics

## Libraries Used

- OpenCV
- MediaPipe
- NumPy

## How It Works

- The webcam tracks your hands in real time
- The left hand controls the left paddle
- The right hand controls the right paddle
- Move your hand up and down to move the paddle
- Make a fist over the START button to begin
- A countdown appears before the ball starts moving
- Make a fist during gameplay to stop the game
- The game resets when the ball goes out of bounds

## Controls

Action | Input
------ | ------
Move paddle | Move hand up/down
Start game | Fist over START button
Stop game | Fist during gameplay
Quit | Press Q

## Requirements

- Python 3.8 or higher
- Webcam
- Good lighting conditions

## Installation

1. Clone the repository:
   git clone https://github.com/rudrashukla7/Computer-Vision-Pong.git
   cd Computer-Vision-Pong

2. Install required libraries:
   pip install opencv-python mediapipe numpy

3. Run the program:
   python pong.py

## Default Settings

- Ball speed: 8
- Paddle height: 80
- Countdown time: 3 seconds

## Future Improvements

- Score tracking system
- Sound effects
- Single-player AI opponent
- Adjustable difficulty
- Improved gesture calibration
