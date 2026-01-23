""" Rudra Shukla
    Computer Vision Pong Game
    Uses hand tracking to control paddles"""

# Import  libraries
import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random

# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize Mediapipe Hand model
mp_hands = mp.solutions.hands
hand = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Game variables
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
max_score = 2
game_started = False
game_start_time = None
countdown_active = False
game_over = False
winner = None
single_player = False
last_fist_time = 0
fist_cooldown = 1.5 
ai_speed = 0.25  
difficulty_selected = False


# Function to detect if hand is in fist position
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

# Main loop
try:
    while cv2.waitKey(1) != ord('q'):
        success, frame = cap.read()

        # Process frame
        if success:
            frame = cv2.flip(frame, 1)
            RGB_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = hand.process(RGB_frame)

            # Reset hover states
            button_hovered = False
            menu_button_hovered = False
            hand_count = 0
            single_player_hovered = False
            two_player_hovered = False
            easy_hovered = False
            medium_hovered = False
            hard_hovered = False
                
            # Hand detection and paddle control
            if result.multi_hand_landmarks:
                hand_count = len(result.multi_hand_landmarks)
                
                for hand_landmarks in result.multi_hand_landmarks:

                    # Move paddles based on hand y position
                    if single_player:
                        if hand_landmarks.landmark[9].x > 0.5:
                            right_paddle_y = int(hand_landmarks.landmark[9].y * 480) - paddle_height // 2
                    else:
                        if hand_landmarks.landmark[9].x < 0.5:
                            left_paddle_y = int(hand_landmarks.landmark[9].y * 480) - paddle_height // 2
                        
                        if hand_landmarks.landmark[9].x > 0.5:
                            right_paddle_y = int(hand_landmarks.landmark[9].y * 480) - paddle_height // 2

                    is_hand_fist = is_fist(hand_landmarks)
                    
                    # Check mode selection buttons
                    hand_x = hand_landmarks.landmark[9].x * 640
                    hand_y = hand_landmarks.landmark[9].y * 480

                    # Pause game if fist detected
                    if game_started and is_hand_fist and not countdown_active and time.time() - last_fist_time > fist_cooldown:
                        game_started = False
                        last_fist_time = time.time()
                    
                    
                    if not game_started and not game_over and left_score == 0 and right_score == 0 and not difficulty_selected:
                        # Single player button
                        if 120 < hand_x < 300 and 180 < hand_y < 280:
                            single_player_hovered = True
                            if is_hand_fist and time.time() - last_fist_time > fist_cooldown:
                                single_player = True
                                difficulty_selected = True
                                last_fist_time = time.time()

                        # Two player button
                        elif 340 < hand_x < 520 and 180 < hand_y < 280:
                            two_player_hovered = True
                            if is_hand_fist and time.time() - last_fist_time > fist_cooldown:
                                single_player = False
                                game_started = True
                                countdown_active = True
                                game_start_time = time.time()
                                last_fist_time = time.time()
                    
                    # Check difficulty selection buttons
                    if difficulty_selected and not game_started and not game_over and left_score == 0 and right_score == 0:
                        # Easy button
                        if 70 < hand_x < 210 and 200 < hand_y < 280:
                            easy_hovered = True
                            if is_hand_fist and time.time() - last_fist_time > fist_cooldown:
                                ai_speed = 0.25
                                game_started = True
                                countdown_active = True
                                game_start_time = time.time()
                                last_fist_time = time.time()

                        # Medium button
                        elif 240 < hand_x < 400 and 200 < hand_y < 280:
                            medium_hovered = True
                            if is_hand_fist and time.time() - last_fist_time > fist_cooldown:
                                ai_speed = 0.55
                                game_started = True
                                countdown_active = True
                                game_start_time = time.time()
                                last_fist_time = time.time()

                        # Hard button
                        elif 430 < hand_x < 570 and 200 < hand_y < 280:
                            hard_hovered = True
                            if is_hand_fist and time.time() - last_fist_time > fist_cooldown:
                                ai_speed = 0.75
                                game_started = True
                                countdown_active = True
                                game_start_time = time.time()
                                last_fist_time = time.time()
                    
                    # Resume button
                    if 120 < hand_landmarks.landmark[9].x * 640 < 300 and 180 < hand_landmarks.landmark[9].y * 480 < 280:
                        button_hovered = True

                        # Resume game if fist on button (when paused with scores)
                        if not game_started and is_hand_fist and not game_over and not (left_score == 0 and right_score == 0) and time.time() - last_fist_time > fist_cooldown:
                            game_started = True
                            countdown_active = True
                            game_start_time = time.time()
                            last_fist_time = time.time()
                    
                    # Menu button
                    if 340 < hand_landmarks.landmark[9].x * 640 < 520 and 180 < hand_landmarks.landmark[9].y * 480 < 280:
                        menu_button_hovered = True
                        
                        # Return to main menu if fist on menu button (when paused)
                        if not game_started and is_hand_fist and not game_over and (left_score > 0 or right_score > 0) and time.time() - last_fist_time > fist_cooldown:
                            left_score = 0
                            right_score = 0
                            ball_pos = [320, 240]
                            ball_velocity = [speed * math.cos(random.uniform(-math.pi/3, math.pi/3)), speed * math.sin(random.uniform(-math.pi/3, math.pi/3))]
                            single_player = False
                            difficulty_selected = False
                            last_fist_time = time.time()
                    
                    # Main menu from game over screen
                    if game_over and is_hand_fist and time.time() - last_fist_time > fist_cooldown:
                        game_over = False
                        winner = None
                        left_score = 0
                        right_score = 0
                        ball_pos = [320, 240]
                        ball_velocity = [speed * math.cos(random.uniform(-math.pi/3, math.pi/3)), speed * math.sin(random.uniform(-math.pi/3, math.pi/3))]
                        game_started = False
                        countdown_active = False
                        single_player = False
                        difficulty_selected = False
                        last_fist_time = time.time()

                    #print(hand_landmarks)
                    #mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Start Menu
            if not game_started and not game_over and left_score == 0 and right_score == 0 and not difficulty_selected:
                # Title
                cv2.putText(frame, "HAND TRACKING PONG", (40, 100), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 215, 255), 2)
                
                # Instructions
                cv2.putText(frame, "Make a FIST to select", (200, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 215, 255), 2)
                cv2.putText(frame, "FIST during game to pause", (170, 155), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 215, 255), 2)
                
                # Single player button
                if single_player_hovered:
                    button_color = (0, 255, 0)
                else:
                    button_color = (0, 215, 255)
                cv2.rectangle(frame, (120, 180), (300, 280), button_color, 5)
                cv2.putText(frame, "1P", (175, 240), cv2.FONT_HERSHEY_COMPLEX, 1.5, button_color, 2)
                
                # Two player button
                if two_player_hovered:
                    button_color = (0, 255, 0)
                else:
                    button_color = (0, 215, 255)
                cv2.rectangle(frame, (340, 180), (520, 280), button_color, 5)
                cv2.putText(frame, "2P", (395, 240), cv2.FONT_HERSHEY_COMPLEX, 1.5, button_color, 2)
                
                # Control instructions
                cv2.putText(frame, "Move hand UP/DOWN to control paddle", (100, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 215, 255), 2)
                cv2.putText(frame, "1P: Right hand controls right paddle", (115, 370), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 215, 255), 2)
                cv2.putText(frame, "2P: Left hand = left, Right hand = right", (90, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 215, 255), 2)
                cv2.putText(frame, "Press Q to Exit Application", (175, 430), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 215, 255), 2)
            
            # Difficulty selection Menu
            elif difficulty_selected and not game_started and not game_over and left_score == 0 and right_score == 0:
                # Title
                cv2.putText(frame, "SELECT DIFFICULTY", (150, 100), cv2.FONT_HERSHEY_COMPLEX, 1.2, (0, 215, 255), 2)
                cv2.putText(frame, "Make a FIST to select", (180, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 215, 255), 2)
                
                # Easy button
                if easy_hovered:
                    button_color = (0, 255, 0)
                else:
                    button_color = (0, 215, 255)
                cv2.rectangle(frame, (70, 200), (210, 280), button_color, 5)
                cv2.putText(frame, "EASY", (100, 250), cv2.FONT_HERSHEY_COMPLEX, 1, button_color, 2)
                
                # Medium button
                if medium_hovered:
                    button_color = (0, 255, 0)
                else:
                    button_color = (0, 215, 255)
                cv2.rectangle(frame, (250, 200), (390, 280), button_color, 5)
                cv2.putText(frame, "MED", (280, 250), cv2.FONT_HERSHEY_COMPLEX, 1, button_color, 2)
                
                # Hard button
                if hard_hovered:
                    button_color = (0, 255, 0)
                else:
                    button_color = (0, 215, 255)
                cv2.rectangle(frame, (430, 200), (570, 280), button_color, 5)
                cv2.putText(frame, "HARD", (455, 250), cv2.FONT_HERSHEY_COMPLEX, 1, button_color, 2)

            # Draw button once after checking all hands
            elif not game_started and not game_over:
                # Resume button (left)
                if button_hovered:
                    button_color = (0, 255, 0)
                else:
                    button_color = (0, 215, 255)
                
                cv2.rectangle(frame, (120, 180), (300, 280), button_color, 5)
                cv2.putText(frame, "Resume", (135, 240), cv2.FONT_HERSHEY_COMPLEX, 1.2, button_color, 2)
                
                # Menu button (right - only show if there are scores)
                if left_score > 0 or right_score > 0:
                    if menu_button_hovered:
                        menu_color = (0, 255, 0)
                    else:
                        menu_color = (0, 215, 255)
                    
                    cv2.rectangle(frame, (340, 180), (520, 280), menu_color, 5)
                    cv2.putText(frame, "Menu", (390, 240), cv2.FONT_HERSHEY_COMPLEX, 1.2, menu_color, 2)
            else:
                # Draw ball and paddles
                cv2.circle(frame, (int(ball_pos[0]), int(ball_pos[1])), ball_radius, (0, 215, 255),-1)
                cv2.rectangle(frame, (10, left_paddle_y), (10 + paddle_width, left_paddle_y + paddle_height), (155, 0, 0), -1)
                cv2.rectangle(frame, (610, right_paddle_y), (610 + paddle_width, right_paddle_y + paddle_height), (0, 0, 155), -1)
            
            # Draw middle dashed line
            for y in range(0, 480, 20):
                cv2.line(frame, (320, y), (320, y + 10), (255, 255, 255), 1)
            
            # Draw scores
            cv2.putText(frame, f"{left_score}", (270, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (155, 0, 0), 3)
            cv2.putText(frame, f"{right_score}", (340, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 155), 3)
            
            # Game over message
            if game_over:
                cv2.rectangle(frame, (100, 150), (540, 330), (0, 215, 255), 3)
                cv2.putText(frame, f"{winner} Wins!", (170, 240), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 255, 0), 3)
                cv2.putText(frame, "Make FIST to return to menu", (110, 295), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 215, 255), 2)
            
            # Countdown timer
            if countdown_active and game_start_time:
                elapsed = time.time() - game_start_time
                remaining = 3 - int(elapsed)
                
                if remaining > 0:
                    cv2.putText(frame, str(remaining), (300, 150), cv2.FONT_HERSHEY_TRIPLEX, 3, (0, 255, 0), 5)
                else:
                    countdown_active = False
                
            
            if game_started and not countdown_active:
                # AI paddle movement
                if single_player:
                    target_y = ball_pos[1] - paddle_height // 2
                    diff = target_y - left_paddle_y
                    left_paddle_y += int(diff * ai_speed)
                    left_paddle_y = max(0, min(400, left_paddle_y))
                
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
                        if single_player:
                            winner = "You" 
                        else: 
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
                        if single_player: 
                            winner = "AI"  
                        else:
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
