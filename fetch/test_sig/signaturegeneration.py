import tkinter as tk
from PIL import Image, ImageDraw

# Set up the drawing window
window = tk.Tk()
window.title("Signature Pad")

# Set the canvas size (adjust as necessary)
canvas_width = 400
canvas_height = 200

# Create a Tkinter canvas
canvas = tk.Canvas(window, width=canvas_width, height=canvas_height, bg="white")
canvas.pack()

# Create a blank image for drawing
image = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))  # Transparent background
draw = ImageDraw.Draw(image)

# Initialize variables to track mouse movement
last_x, last_y = None, None

# Function to start drawing when the mouse button is pressed
def activate_paint(event):
    global last_x, last_y
    last_x, last_y = event.x, event.y

# Function to draw on the canvas as the mouse moves
def paint(event):
    global last_x, last_y
    if last_x and last_y:
        # Draw on the Tkinter canvas
        canvas.create_line(last_x, last_y, event.x, event.y, width=3, fill="black", capstyle=tk.ROUND, smooth=tk.TRUE)
        # Draw on the PIL image
        draw.line((last_x, last_y, event.x, event.y), fill="black", width=3)
        last_x, last_y = event.x, event.y

# Function to save the image as a transparent PNG
def save_image():
    filename = "signature.png"
    image.save(filename)
    print(f"Signature saved as {filename}")

# Bind the mouse events to the canvas
canvas.bind("<Button-1>", activate_paint)  # Left mouse button pressed
canvas.bind("<B1-Motion>", paint)  # Mouse movement with button held down

# Add a button to save the image
save_button = tk.Button(window, text="Save Signature", command=save_image)
save_button.pack()

# Start the Tkinter event loop
window.mainloop()

