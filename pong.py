import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

mp_hands = mp.solutions.hands
hand = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils


ball_pos = [320, 240]
speed = 8
ball_velocity = [speed * math.cos(random.uniform(-math.pi/3, math.pi/3)), speed * math.sin(random.uniform(-math.pi/3, math.pi/3))]
ball_radius = 5
paddle_width = 20
paddle_height = 80

left_paddle_y = 200
right_paddle_y = 200

left_score = 0
right_score = 0
max_score = 7

game_started = False
game_start_time = None
countdown_active = False
game_over = False
winner = None



def is_fist(hand_landmarks):

    fingertip_indices = [4, 8, 12, 16, 20]
    pip_indices = [3, 7, 11, 15, 19]
    
    fingers_bent = 0
    
    for tip_idx, pip_idx in zip(fingertip_indices, pip_indices):
        tip = hand_landmarks.landmark[tip_idx]
        pip = hand_landmarks.landmark[pip_idx]
        
        if tip.y > pip.y:
            fingers_bent += 1
    
    return fingers_bent >= 4

try:
    while cv2.waitKey(1) != ord('q'):
        success, frame = cap.read()
        if success:
            frame = cv2.flip(frame, 1)
            RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hand.process(RGB_frame)

            
            button_hovered = False
            hand_count = 0
                
            if result.multi_hand_landmarks:
                hand_count = len(result.multi_hand_landmarks)
                
                for hand_landmarks in result.multi_hand_landmarks:

                    # Move paddles based on hand y position
                    if hand_landmarks.landmark[9].x < 0.5:
                        left_paddle_y = int(hand_landmarks.landmark[9].y * 480) - paddle_height // 2
                    
                    if hand_landmarks.landmark[9].x > 0.5:
                        right_paddle_y = int(hand_landmarks.landmark[9].y * 480) - paddle_height // 2

                    is_hand_fist = is_fist(hand_landmarks)
                    
                    if game_started and is_hand_fist and not countdown_active:
                        game_started = False
                    
                    # Check if hand is over button
                    if 220 < hand_landmarks.landmark[9].x * 640 < 420 and 180 < hand_landmarks.landmark[9].y * 480 < 280:
                        button_hovered = True
                        # Start game if fist on button
                        if not game_started and is_hand_fist and not game_over:
                            game_started = True
                            countdown_active = True
                            game_start_time = time.time()
                        # Restart game if fist on button when game is over
                        if game_over and is_hand_fist:
                            game_over = False
                            winner = None
                            left_score = 0
                            right_score = 0
                            ball_pos = [320, 240]
                            ball_velocity = [speed * math.cos(random.uniform(-math.pi/3, math.pi/3)), speed * math.sin(random.uniform(-math.pi/3, math.pi/3))]
                            game_started = True
                            countdown_active = True
                            game_start_time = time.time()

                    #print(hand_landmarks)
                    #mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Draw button once after checking all hands
            if not game_started and not game_over:
                button_color = (0, 255, 0) if button_hovered else (0, 0, 0)
                cv2.rectangle(frame, (220, 180), (420, 280), button_color, 5)
                cv2.putText(frame, "START", (245, 230), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 3)
            else:
                # Draw ball and paddles
                cv2.circle(frame, (int(ball_pos[0]), int(ball_pos[1])), ball_radius, (255,255,255),-1)
                cv2.rectangle(frame, (10, left_paddle_y), (10 + paddle_width, left_paddle_y + paddle_height), (155, 0, 0), -1)
                cv2.rectangle(frame, (610, right_paddle_y), (610 + paddle_width, right_paddle_y + paddle_height), (0, 0, 155), -1)
            
            # Draw middle dashed line
            for y in range(0, 480, 20):
                cv2.line(frame, (320, y), (320, y + 10), (255, 255, 255), 1)
            
            # Draw scores
            cv2.putText(frame, f"Left: {left_score}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (155, 0, 0), 2)
            cv2.putText(frame, f"Right: {right_score}", (450, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 155), 2)
            
            # Display game over message
            if game_over:
                cv2.rectangle(frame, (100, 150), (540, 330), (0, 0, 0), -1)
                cv2.putText(frame, f"{winner} Wins!", (150, 240), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)
                cv2.putText(frame, "Fist to restart", (140, 290), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
            
            # Countdown timer
            if countdown_active and game_start_time:
                elapsed = time.time() - game_start_time
                remaining = 3 - int(elapsed)
                
                if remaining > 0:
                    cv2.putText(frame, str(remaining), (300, 150), cv2.FONT_HERSHEY_TRIPLEX, 3, (0, 255, 0), 5)
                else:
                    countdown_active = False
                
            
            if game_started and not countdown_active:
                # Update ball position
                ball_pos[0] += ball_velocity[0]
                ball_pos[1] += ball_velocity[1]

                # Bounce off top and bottom walls
                if ball_pos[1] - ball_radius <= 0:
                    ball_velocity[1] = -ball_velocity[1]
                    ball_pos[1] = ball_radius 
                elif ball_pos[1] + ball_radius >= 480:
                    ball_velocity[1] = -ball_velocity[1]
                    ball_pos[1] = 480 - ball_radius 

                # Bounce off left paddle
                if (ball_pos[0] - ball_radius <= 25 and left_paddle_y <= ball_pos[1] <= left_paddle_y + paddle_height):
                    # Calculate where ball hit on paddle (0 = bottom, 1 = top)
                    hit_pos = (ball_pos[1] - left_paddle_y) / paddle_height
                    angle_offset = (hit_pos - 0.5) * 3  
                    ball_velocity[0] = abs(ball_velocity[0]) + 1
                    ball_velocity[1] += angle_offset * 3
                    ball_pos[0] = 25 + ball_radius  

                # Bounce off right paddle
                if (ball_pos[0] + ball_radius >= 615 and right_paddle_y <= ball_pos[1] <= right_paddle_y + paddle_height):
                    # Calculate where ball hit on paddle (0 = bottom, 1 = top)
                    hit_pos = (ball_pos[1] - right_paddle_y) / paddle_height
                    angle_offset = (hit_pos - 0.5) * 3  
                    ball_velocity[0] = -(abs(ball_velocity[0]) + 1)
                    ball_velocity[1] += angle_offset * 3
                    ball_pos[0] = 615 - ball_radius 

                # Score and reset
                if ball_pos[0] < 0:
                    right_score += 1
                    if right_score >= max_score:
                        game_over = True
                        winner = "Right"
                        game_started = False
                    else:
                        ball_pos = [320, 240]
                        ball_velocity = [speed * math.cos(random.uniform(-math.pi/3, math.pi/3)), speed * math.sin(random.uniform(-math.pi/3, math.pi/3))]
                        game_started = False
                elif ball_pos[0] > 640:
                    left_score += 1
                    if left_score >= max_score:
                        game_over = True
                        winner = "Left"
                        game_started = False
                    else:
                        ball_pos = [320, 240]
                        ball_velocity = [speed * math.cos(random.uniform(-math.pi/3, math.pi/3)), speed * math.sin(random.uniform(-math.pi/3, math.pi/3))]
                        game_started = False

            cv2.imshow("capture image",frame)
finally:
    cap.release()
    hand.close()        
    cv2.destroyAllWindows()    

