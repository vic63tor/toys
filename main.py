#!/usr/bin/env python3
import wechatbot
import tkinter as tk
from PIL import Image, ImageTk
import sys

def on_closing():
    print("Window closed")

def main_window():
    root = tk.Tk()
    root.title("My App")
    root.geometry("400x300")
    label = tk.Label(root, text="Welcome to My App")
    label.pack(pady=20)
    
    image = Image.open("resources/images/my_image.jpg")
    photo = ImageTk.PhotoImage(image)
    image_label = tk.Label(root, image=photo)
    image_label.pack()

    root.mainloop()
'''
To ask for an environment variable using Flask, you can use the os module to access environment variables and the request object to handle user input. Here's an example code snippet that should accomplish what you're trying to do:

python
Copy code
import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    var_name = 'MY_VAR_NAME'
    env_var = os.environ.get(var_name)
    
    if env_var:
        # If the environment variable exists, display it
        return f"The value of {var_name} is {env_var}"
    else:
        # If the environment variable doesn't exist, ask the user to enter it
        return f"Please enter the value of {var_name}: <form method='POST'><input name='env_var'><input type='submit'></form>"

@app.route('/', methods=['POST'])
def save_env_var():
    var_name = 'MY_VAR_NAME'
    env_var = request.form['env_var']
    
    # Save the environment variable
    os.environ[var_name] = env_var
    
    # Display the saved value
    return f"The value of {var_name} is {env_var}"

if __name__ == '__main__':
    app.run()
In this code, the home() function first checks if the environment variable MY_VAR_NAME exists. If it does, the function displays its value. If not, the function displays a form asking the user to enter the value.

When the user submits the form, the save_env_var() function is called. This function retrieves the value from the form, saves it as an environment variable, and displays the saved value.

Note that this code only saves the environment variable for the current instance of the Flask application. If you want to make the environment variable persistent, you'll need to modify the code to save it in a configuration file or a database.
'''
if __name__ == '__main__':
    print(sys.path)
    quit()
    wechatinstance = wechat.wechatHandler()
    print(wechatinstance.tmpDir)
    #main_window()
    #itchat.run(debug=True, blockThread=True)