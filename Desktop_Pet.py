import tkinter as tk
import time
import random
from pynput.mouse import Controller, Listener

class Pet:
    def __init__(self):
        # Create a window
        self.window = tk.Tk()

        self.screen_width = self.window.winfo_screenwidth()
        self.screen_height = self.window.winfo_screenheight()

        print(f"Desktop size: {self.screen_width} x {self.screen_height} pixels")

        # Placeholder images for walking right and left
        self.walking_right = [tk.PhotoImage(file='walking_right.gif', format='gif -index %i' % i) for i in range(4)]
        self.walking_left = [tk.PhotoImage(file='walking_left.gif', format='gif -index %i' % i) for i in range(4)]

        self.frame_index = 0
        self.img = self.walking_right[self.frame_index]

        # Timestamp to check whether to advance frame
        self.timestamp = time.time()

        # Set focus highlight to black when the window does not have focus
        self.window.config(highlightbackground='black')

        # Make window frameless
        self.window.overrideredirect(True)

        # Make window draw over all others
        self.window.attributes('-topmost', True)

        # Turn black into transparency
        self.window.wm_attributes('-transparentcolor', 'black')

        # Create a label as a container for our image
        self.label = tk.Label(self.window, bd=0, bg='black')

        # Create a window of size 64x64 pixels, at coordinates 0,0
        self.x = 0
        self.y = self.screen_height - 120
        self.window.geometry('64x64+{x}+{y}'.format(x=str(self.x), y=str(self.y)))
        self.walk_right = True

        # Jump variables
        self.is_jumping = False
        self.jump_height = 10  # Height of the jump
        self.jump_count = 0     # Counter for the jump

        # Running control variables
        self.running_time = 5  # Time in seconds the pet can run before getting tired
        self.resting_time = 3   # Time in seconds the pet needs to rest
        self.is_running = True   # Flag to check if the pet is running
        self.run_start_time = time.time()  # Time when the pet started running

        # Add the image to our label
        self.label.configure(image=self.img)

        # Give window to geometry manager (so it will appear)
        self.label.pack()

        self.window.bind("<space>", lambda event: self.jump())  # Bind spacebar to jump action

        # Initialize pynput mouse controller
        self.mouse = Controller()

        # Variables to track mouse button state
        self.mouse_button_pressed = False

        # Start mouse listener
        self.listener = Listener(on_click=self.on_click)
        self.listener.start()

        # Run self.update() after 0ms when mainloop starts
        self.window.after(0, self.update)
        self.window.mainloop()

    def on_click(self, x, y, button, pressed):
        self.mouse_button_pressed = pressed

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_count = self.jump_height

    def check_collision_with_mouse(self):
        # Get current mouse position
        mouse_x, mouse_y = self.mouse.position
        
        # Check for collision
        if (self.x < mouse_x < self.x + 64) and (self.y < mouse_y < self.y + 64):
            return True
        return False

    def update(self):
        # Print the current position
        print(f"Position: {self.x}, {self.y}")

        # Determine speed based on mouse possession
        speed = 2 if self.mouse_button_pressed else 1  # Double speed when mouse is held down

        # Always move when in possession of the mouse
        if self.mouse_button_pressed:
            if self.walk_right:
                new_x = self.x + speed
                if new_x <= self.screen_width - 64:  # Check right boundary
                    self.x = new_x
                self.img = self.walking_right[self.frame_index]
            else:
                new_x = self.x - speed
                if new_x >= 0:  # Check left boundary
                    self.x = new_x
                self.img = self.walking_left[self.frame_index]
        else:
            # Handle running/resting logic when not in possession of the mouse
            if self.is_running:
                if time.time() - self.run_start_time < self.running_time:
                    # Move as long as the pet is not tired
                    if self.walk_right:
                        new_x = self.x + speed
                        if new_x <= self.screen_width - 64:  # Check right boundary
                            self.x = new_x
                        self.img = self.walking_right[self.frame_index]
                    else:
                        new_x = self.x - speed
                        if new_x >= 0:  # Check left boundary
                            self.x = new_x
                        self.img = self.walking_left[self.frame_index]
                else:
                    # Start resting after running time is over
                    self.is_running = False
                    self.run_start_time = time.time()  # Reset the timer for resting

            else:
                # Handle resting
                if time.time() - self.run_start_time < self.resting_time:
                    # Pet does not move while resting
                    pass
                else:
                    # After resting, the pet starts running again
                    self.is_running = True
                    self.run_start_time = time.time()  # Reset the running timer

            # Randomly decide to change direction
            if random.random() < 0.001:  # 0.1% chance to change direction
                self.walk_right = not self.walk_right

        # Check if the pet collides with the mouse
        if self.check_collision_with_mouse():
            # Move the mouse cursor to the pet's position
            self.mouse.position = (self.x + 32, self.y + 32)  # Center the cursor on the pet

        # Check if it's time to jump randomly
        if not self.is_jumping and random.random() < 0.01:  # Adjust probability for random jumps
            self.jump()

        # Handle jumping
        if self.is_jumping:
            if self.jump_count >= 0:
                self.y -= (self.jump_height - self.jump_count)  # Move up
                self.jump_count -= 1
            else:
                self.is_jumping = False  # End jump
                self.jump_count = 0

        # Update y position for falling
        if not self.is_jumping and self.y < self.screen_height - 120:
            self.y += 2  # Falling speed
            if self.y >= self.screen_height - 120:
                self.y = self.screen_height - 120  # Reset to ground level

        # Advance frame if 50ms have passed
        if time.time() > self.timestamp + 0.05:
            self.timestamp = time.time()
            self.frame_index = (self.frame_index + 1) % 4  # Cycle through frames

        # Update window position and image
        self.window.geometry('64x64+{x}+{y}'.format(x=str(self.x), y=str(self.y)))
        self.label.configure(image=self.img)

        # Call update after 10ms
        self.window.after(10, self.update)

Pet()
