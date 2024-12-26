import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox, Checkbutton

def getCDF(in_img):
    """根据归一化直方图计算累积分布函数 (CDF)"""
    hist, _ = np.histogram(in_img, bins=256, range=(0, 256), density=True)
    return hist.cumsum()

def hist_match(source, target):
    source_cdf = getCDF(source)
    target_cdf = getCDF(target)
    
    mapping = np.zeros(256, dtype=np.uint8)
    for src_pixel in range(256):
        closest_pixel = np.argmin(np.abs(target_cdf - source_cdf[src_pixel]))
        mapping[src_pixel] = closest_pixel

    matched = mapping[source.flatten()]
    return matched.reshape(source.shape), mapping

def export_mapping(maps, mode):
    """导出映射表为 PNG 图片"""
    map_img = np.stack(maps, axis=0)  # 堆叠 R/G/B 或 H/S/V
    img = Image.fromarray(map_img.astype(np.uint8))
    save_path = filedialog.asksaveasfilename(defaultextension=".png", 
                                             filetypes=[("PNG files", "*.png")], 
                                             title="Save Mapping")
    if save_path:
        img.save(save_path)
        messagebox.showinfo("Success", f"Mapping exported to {save_path}")

def process_images():
    global matched_img
    if not source_img or not target_img:
        messagebox.showerror("Error", "Please select both source and target images.")
        return

    # 获取处理模式和通道选择
    mode = mode_combo.get()
    selected_channels = [var_r.get(), var_g.get(), var_b.get()]

    # 转换图像为数组
    source_arr = np.asarray(source_img.convert('RGB'))
    target_arr = np.asarray(target_img.convert('RGB'))

    if mode == "HSV":
        source_arr = np.asarray(source_img.convert('HSV'))
        target_arr = np.asarray(target_img.convert('HSV'))

    channels = ['H', 'S', 'V'] if mode == "HSV" else ['R', 'G', 'B']

    # 初始化映射表
    maps = []
    matched_channels = []

    for i, selected in enumerate(selected_channels):
        if selected:
            matched, mapping = hist_match(source_arr[:, :, i], target_arr[:, :, i])
            matched_channels.append(matched)
            maps.append(mapping)
        else:
            matched_channels.append(source_arr[:, :, i])
            maps.append(np.arange(256, dtype=np.uint8))
    # 合并处理后的通道
    matched_arr = np.stack(matched_channels, axis=-1)
    matched_img = Image.fromarray(matched_arr.astype('uint8'), mode='HSV' if mode == "HSV" else 'RGB').convert('RGB')

    # 更新显示
    show_images()

    # 导出映射表
    if messagebox.askyesno("Export", f"Export {mode} Mapping Table?"):
        export_mapping(maps, mode)

def show_images():
    """更新显示的图像"""
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(source_img)
    axes[0].set_title("Source Image")
    axes[0].axis('off')

    axes[1].imshow(target_img)
    axes[1].set_title("Target Image")
    axes[1].axis('off')

    axes[2].imshow(matched_img)
    axes[2].set_title("Matched Image")
    axes[2].axis('off')

    plt.show()

def load_source_image():
    global source_img
    path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if path:
        source_img = Image.open(path)
        source_label.config(text=f"Source Image: {path.split('/')[-1]}")

def load_target_image():
    global target_img
    path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")])
    if path:
        target_img = Image.open(path)
        target_label.config(text=f"Target Image: {path.split('/')[-1]}")

# 初始化全局变量
source_img = None
target_img = None
matched_img = None

# 创建主窗口
root = tk.Tk()
root.title("Histogram Matching Tool")
root.geometry("500x400")

# 模式选择
mode_label = tk.Label(root, text="Select Mode:")
mode_label.pack()
mode_combo = Combobox(root, values=["RGB", "HSV"])
mode_combo.current(0)
mode_combo.pack()

# 通道选择
channel_frame = tk.Frame(root)
channel_frame.pack()
var_r = tk.BooleanVar(value=True)
var_g = tk.BooleanVar(value=True)
var_b = tk.BooleanVar(value=True)

check_r = Checkbutton(channel_frame, text="R/H", variable=var_r)
check_r.grid(row=0, column=0)
check_g = Checkbutton(channel_frame, text="G/S", variable=var_g)
check_g.grid(row=0, column=1)
check_b = Checkbutton(channel_frame, text="B/V", variable=var_b)
check_b.grid(row=0, column=2)

# 图片加载按钮
source_button = tk.Button(root, text="Load Source Image", command=load_source_image)
source_button.pack()
source_label = tk.Label(root, text="Source Image: None")
source_label.pack()

target_button = tk.Button(root, text="Load Target Image", command=load_target_image)
target_button.pack()
target_label = tk.Label(root, text="Target Image: None")
target_label.pack()

# 处理按钮
process_button = tk.Button(root, text="Process Images", command=process_images)
process_button.pack()

# 运行主循环
root.mainloop()
