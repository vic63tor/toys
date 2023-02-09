#!/usr/bin/env python3
import wechatGPT
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

if __name__ == '__main__':
    print(sys.path)
    quit()
    wechatinstance = wechat.wechatHandler()
    print(wechatinstance.tmpDir)
    #main_window()
    #itchat.run(debug=True, blockThread=True)