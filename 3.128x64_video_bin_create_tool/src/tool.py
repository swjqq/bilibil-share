import tkinter.ttk
from tkinter import *
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk
import glob
import os
import tkinter.messagebox  #这个是消息框，对话框的关键
import cv2
import numpy
from PIL import Image, ImageDraw

# 输出文件路径
output_path = "./output/"
output_name = "video.bin"
output_video_bin_path = output_path + output_name
if not os.path.exists(output_path):
    os.makedirs(output_path)

# 原始图片(RGB)路径
original_images_path = []
original_images_count = 0

# 灰度图片路径
gray_images_dir_path = "./cache/gray/"
if not os.path.exists(gray_images_dir_path):
    os.makedirs(gray_images_dir_path)

gray_images_path = []
gray_images_count = 0

# 二值图保存路径
binary_images_dir_path = "./cache/binary/"
if not os.path.exists(binary_images_dir_path):
    os.makedirs(binary_images_dir_path)

binary_images_path = []
binary_images_count = 0
binary_threshold_value = []

# 当前正在处理的图片索引
cur_process_img_index = 0
cur_img_gray = None
cur_img_gray_save_path = ""
cur_img_binary = None
cur_img_binary_save_path = ""
cur_img_binary_threshold_value = 0


def get_images_path(dir_path, pic_format):
    """获取某一文件夹下所有指定格式图片的绝对路径

    Args:
        dir_path (str): 图片文件夹路径
        pic_format (str): 图片格式: bmp, png, jpg...

    Returns:
        tuple: (该目录下所有指定格式图片的绝对路径, 图片总数)
        
    """

    images_path = glob.glob(dir_path + "\\*" + pic_format)
    return (images_path, len(images_path))


def get_gray_image(img, img_name, save=False):
    """生成一张灰度图并保存

    Args:
        img (Image): 图片
        img_name (str): 图片名字
        
    Returns:
        tuple: (灰度图, 灰度图名字, 保存时的绝对路径) 
    """

    img_gray = img.convert("L")
    img_gray_name = "gray_" + img_name

    img_gray_save_path = gray_images_dir_path + img_gray_name

    if save:
        img_gray.save(img_gray_save_path)

    return (img_gray, img_gray_name, img_gray_save_path)


def get_binary_image(img_gray,
                     img_gray_name,
                     thresh=127,
                     maxval=255,
                     type=cv2.THRESH_OTSU,
                     save=False):
    """生成一张灰度图并保存

    Args:
        img_gray (Image): 灰度图片
        img_gray_name (str): 灰度图片名字
        invert (bool) : 是否反转
        
    Returns:
        tuple: (二值图, 二值图名字, 阈值, 保存时的绝对路径) 
    """

    img_binary_name = img_gray_name.replace("gray", "binary")

    _threshold_value, img_binary = cv2.threshold(numpy.asarray(img_gray),
                                                 thresh, maxval, type)

    # OpenCV 转 PIL
    img_binary = Image.fromarray(img_binary)

    img_binary_save_path = binary_images_dir_path + img_binary_name

    if save:
        img_binary.save(img_binary_save_path)

    return (img_binary, img_binary_name, _threshold_value,
            img_binary_save_path)


def get_image_name(image_path):
    """根据路径获取图片名字

    Args:
        image_path (str): 图片路径

    Returns:
        srt: 图片名字
    """
    image_name = image_path.split("\\")[-1]
    return image_name


def update_image_label(image_label, text_label, img, img_name):
    """更新图片及其题注显示

    Args:
        image_label ([type]): 图片标签句柄
        text_label ([type]): 题注标签句柄
        img (Image): 图片
        img_name (str): 图片名字
    """

    photo = ImageTk.PhotoImage(img)
    image_label.config(image=photo)
    image_label.image = photo
    text_label["text"] = img_name

    root.update()


def get_pixel_intensity(pixel, invert=False, max_value=255):
    """
    Gets the average intensity of a pixel.
    """
    intensity = 0

    # Pixel is multi channel
    if type(pixel) is list or type(pixel) is tuple:
        for channel_intensity in pixel:
            intensity += channel_intensity
        intensity /= len(pixel)
    # Pixel is single channel
    elif type(pixel) is int or type(pixel) is float:
        intensity = pixel
    # Pixel is magic
    else:
        raise ValueError('Not a clue what format the pixel data is: ' +
                         str(type(pixel)))

    if invert:
        return max_value - intensity
    else:
        return intensity


def get_average_pixel_intensity(width, height, pixel_data, invert):
    """
    Gets the average intensity over all pixels.
    """

    avg_intensity = 0

    for x_idx in range(0, width):
        for y_idx in range(0, height):
            avg_intensity += get_pixel_intensity(pixel_data[x_idx, y_idx],
                                                 invert)

    avg_intensity = avg_intensity / (width * height)

    return avg_intensity


def reverse_bit(dat):
    res = 0
    for i in range(0, 8, 1):
        res = res << 1
        res = res | (dat & 1)
        dat = dat >> 1
    return res


def output_image_c_array(width, height, pixel_data, crossover, invert):
    """
    Outputs the data in a C bitmap array format.
    """

    ret = []

    for y_idx in range(0, height):
        next_line = ''
        next_value = 0

        for x_idx in range(0, width):
            if (x_idx % 8 == 0 or x_idx == width - 1) and x_idx > 0:
                next_value = reverse_bit(next_value)
                next_line += str('0x%0.2X' % next_value).lower() + ","
                ret.append(next_value)
                next_value = 0

            if get_pixel_intensity(pixel_data[x_idx, y_idx],
                                   invert) > crossover:
                next_value += 2**(7 - (x_idx % 8))

    return ret


def convert(image, output_path="./video.bin", threshold=0, invert=False):
    """
    Runs an image conversion.
    """

    image_data = image.load()

    width = image.size[0]
    height = image.size[1]

    if threshold == 0:
        crossover_intensity = get_average_pixel_intensity(
            width, height, image_data, invert)
    else:
        crossover_intensity = threshold
    ret = output_image_c_array(width, height, image_data, crossover_intensity,
                               invert)

    with open(output_path, "ab+") as f:
        f.write(bytearray(ret))  # 自带文件关闭功能，不需要再写f.close()


def select_path():
    """设置原始图片文件夹路径
    """
    path_ = askdirectory()  #使用askdirectory()方法返回文件夹的路径
    if path_ == "":
        path.get()  #当打开文件路径选择框后点击"取消" 输入框会清空路径，所以使用get()方法再获取一次路径
    else:
        path_ = path_.replace("/", "\\")  # 实际在代码中执行的路径为“\“ 所以替换一下
        path.set(path_)
        print(path_)

        # 扫描所有图片
        global original_images_path, original_images_count
        original_images_path, original_images_count = get_images_path(
            path.get(), picture_format.get())

        if original_images_count == 0:
            tkinter.messagebox.showerror('错误', '不存在所选格式图片,  请检查图片格式!')
        else:
            # 显示第一张图片
            global cur_process_img_index
            cur_process_img_index = 0

            process_current_image()

            scale_cur_img.config(to=original_images_count - 1)
            scale_cur_img.set(cur_process_img_index)  # 设置初始值

            global binary_threshold_value
            binary_threshold_value = [0] * original_images_count


# img = Image.open(original_images_path[cur_process_img_index])
# img_name = get_image_name(
#     original_images_path[cur_process_img_index])

# img_gray, img_gray_name, _ = get_gray_image(img, img_name)

# img_binary, img_binary_name, _threshold_value, _ = get_binary_image(
#     img_gray, img_gray_name)

# # 更新显示窗口
# update_image_label(origin_label_image, origin_label_text, img,
#                    img_name)
# update_image_label(gray_label_image, gray_label_text, img_gray,
#                    img_gray_name)
# update_image_label(binary_label_image, binary_label_text,
#                    img_binary, img_binary_name)

# cur_process_img_index += 1


def batch_grayscale():
    """批量灰度化
    """
    if path.get() == "请选择图片所在文件夹":
        tkinter.messagebox.showerror('错误', '请先选择图片文件夹路径和图片格式!')
        return
    if original_images_count == 0:
        tkinter.messagebox.showerror('错误', '不存在所选格式图片,  请检查图片格式!')
        return

    # 进度值最大值
    progressbar_batch_grayscale['maximum'] = original_images_count
    # 进度值初始值
    progressbar_batch_grayscale['value'] = 0

    global cur_process_img_index
    cur_process_img_index = 0
    # scale_cur_img.set(cur_process_img_index)  # 设置初始值

    for i in original_images_path:
        img = Image.open(i)
        img_name = get_image_name(i)

        img_gray, img_gray_name, _ = get_gray_image(img, img_name, save=True)

        # 更新显示窗口
        progressbar_batch_grayscale['value'] += 1
        cur_process_img_index += 1
        # scale_cur_img.set(cur_process_img_index)  # 设置初始值

        update_image_label(origin_label_image, origin_label_text, img,
                           img_name)
        update_image_label(gray_label_image, gray_label_text, img_gray,
                           img_gray_name)

    global gray_images_path, gray_images_count
    gray_images_path, gray_images_count = get_images_path(
        gray_images_dir_path, picture_format.get())

    tkinter.messagebox.showinfo('提示', '批量灰度化完成')


def batch_binarization():
    """批量二值化
    """
    if path.get() == "请选择图片所在文件夹":
        tkinter.messagebox.showerror('错误', '请先选择图片文件夹路径和图片格式!')
        return
    if original_images_count == 0:
        tkinter.messagebox.showerror('错误', '不存在所选格式图片,  请检查图片格式!')
        return
    if gray_images_count == 0:
        tkinter.messagebox.showerror('错误', '请先进行批量灰度化!')
        return

    # 进度值最大值
    progressbar_batch_binarization['maximum'] = gray_images_count
    # 进度值初始值
    progressbar_batch_binarization['value'] = 0
    """
    cv2.THRESH_BINARY       如果 src(x,y)>threshold, dst(x,y) = max_value; 否则,dst（x,y）=0
    cv2.THRESH_BINARY_INV   如果 src(x,y)>threshold, dst(x,y) = 0; 否则,dst(x,y) = max_value
    cv2.THRESH_TRUNC        如果 src(x,y)>threshold, dst(x,y) = max_value; 否则dst(x,y) = src(x,y)
    cv2.THRESH_TOZERO       如果 src(x,y)>threshold, dst(x,y) = src(x,y) ; 否则 dst(x,y) = 0
    cv2.THRESH_TOZERO_INV   如果 src(x,y)>threshold, dst(x,y) = 0 ; 否则dst(x,y) = src(x,y)
    """

    global cur_process_img_index
    cur_process_img_index = 0
    # scale_cur_img.set(cur_process_img_index)  # 设置初始值

    for i in gray_images_path:
        img_gray = Image.open(i)
        img_gray_name = get_image_name(i)

        if binary_type.get() == "THRESH_OTSU":
            type = cv2.THRESH_OTSU
        elif binary_type.get() == "THRESH_OTSU_INV":
            type = cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV
        elif binary_type.get() == "THRESH_BINARY":
            type = cv2.THRESH_BINARY
        elif binary_type.get() == "THRESH_BINARY_INV":
            type = cv2.THRESH_BINARY_INV
        elif binary_type.get() == "THRESH_TRUNC":
            type = cv2.THRESH_TRUNC
        elif binary_type.get() == "THRESH_TOZERO":
            type = cv2.THRESH_TOZERO
        elif binary_type.get() == "THRESH_TOZERO_INV":
            type = cv2.THRESH_TOZERO_INV

        img_binary, img_binary_name, _threshold_value, _ = get_binary_image(
            img_gray,
            img_gray_name,
            thresh=threshold_value.get(),
            type=type,
            save=True)

        binary_threshold_value.append(_threshold_value)
        # 更新显示窗口
        progressbar_batch_binarization['value'] += 1

        cur_process_img_index += 1
        # scale_cur_img.set(cur_process_img_index)  # 设置初始值

        update_image_label(gray_label_image, gray_label_text, img_gray,
                           img_gray_name)
        update_image_label(binary_label_image, binary_label_text, img_binary,
                           img_binary_name)

    global binary_images_path, binary_images_count
    binary_images_path, binary_images_count = get_images_path(
        binary_images_dir_path, picture_format.get())

    tkinter.messagebox.showinfo('提示', '全部二值化完成')


root = Tk()
root.title("序列图转128x64字模小工具")

# 显示图片
img_open = Image.new('RGB', (128, 64), (255, 255, 255))
draw = ImageDraw.Draw(img_open)
draw.text((48, 26), 'origin', fill="#ff0000")
origin_image = ImageTk.PhotoImage(img_open)
origin_label_image = Label(root, image=origin_image)
origin_label_image.grid(row=1, column=0, rowspan=2)
origin_label_text = Label(root, text="原图")
origin_label_text.grid(row=3, column=0)

img_open = Image.new('RGB', (128, 64), (255, 255, 255))
draw = ImageDraw.Draw(img_open)
draw.text((52, 26), 'gray', fill="#ff0000")
gray_image = ImageTk.PhotoImage(img_open)
gray_label_image = Label(root, image=gray_image)
gray_label_image.grid(row=1, column=1, rowspan=2)
gray_label_text = Label(root, text="灰度图")
gray_label_text.grid(row=3, column=1)

img_open = Image.new('RGB', (128, 64), (255, 255, 255))
draw = ImageDraw.Draw(img_open)
draw.text((48, 26), 'binary', fill="#ff0000")
binary_image = ImageTk.PhotoImage(img_open)
binary_label_image = Label(root, image=binary_image)
binary_label_image.grid(row=1, column=2, rowspan=2)
binary_label_text = Label(root, text="二值图")
binary_label_text.grid(row=3, column=2)

path = StringVar()
path.set("请选择图片所在文件夹")
# path.set(os.path.abspath("."))

Entry(root, textvariable=path, state="readonly").grid(row=0,
                                                      column=0,
                                                      columnspan=3,
                                                      padx=2,
                                                      pady=3,
                                                      sticky=E + N + S + W)

Button(root, text="设置文件夹", command=select_path).grid(row=0,
                                                     column=3,
                                                     sticky=E + W)


# 创建下拉菜单 图片格式选择
def pictureFormatChange(selected):
    # 重新获取图片路径
    global original_images_path, original_images_count
    original_images_path, original_images_count = get_images_path(
        path.get(), picture_format.get())

    print(original_images_path, original_images_count)


picture_format_list = ('bmp', 'png', 'jpg')
picture_format = StringVar()
picture_format.set(picture_format_list[0])  # 默认设置为bmp

OptionMenu(root,
           picture_format,
           *picture_format_list,
           command=pictureFormatChange).grid(row=0,
                                             column=4,
                                             sticky=E + W + N + S,
                                             padx=2,
                                             pady=3)

button_batch_grayscale = Button(root, text="全部灰度化", command=batch_grayscale)
button_batch_grayscale.grid(row=1, column=3, sticky=E + W)

progressbar_batch_grayscale = tkinter.ttk.Progressbar(root)
progressbar_batch_grayscale.grid(row=1, column=4, sticky=E + W, padx=3)

button_batch_binarization = Button(root,
                                   text="全部二值化",
                                   command=batch_binarization)
button_batch_binarization.grid(row=2, column=3, sticky=E + W)

progressbar_batch_binarization = tkinter.ttk.Progressbar(root)
progressbar_batch_binarization.grid(row=2, column=4, sticky=E + W, padx=3)

# 批量二值化范围
entry_part_binarization_from = Entry(root, state="normal")
entry_part_binarization_from.grid(row=0, column=6, sticky=E + W, padx=3)

entry_part_binarization_from.grid_remove()
entry_part_binarization_to = Entry(root, state="normal")
entry_part_binarization_to.grid(row=0, column=7, sticky=E + W, padx=3)
entry_part_binarization_to.grid_remove()


def part_binarization():
    """范围二值化
    """
    if path.get() == "请选择图片所在文件夹":
        tkinter.messagebox.showerror('错误', '请先选择图片文件夹路径和图片格式!')
        return
    if original_images_count == 0:
        tkinter.messagebox.showerror('错误', '不存在所选格式图片,  请检查图片格式!')
        return
    if gray_images_count == 0:
        tkinter.messagebox.showerror('错误', '请先进行批量灰度化!')
        return

    process_from = int(entry_part_binarization_from.get())
    process_to = int(entry_part_binarization_to.get())

    # 进度值最大值
    progressbar_part_binarization['maximum'] = process_to - process_from
    # 进度值初始值
    progressbar_part_binarization['value'] = 0
    """
    cv2.THRESH_BINARY       如果 src(x,y)>threshold, dst(x,y) = max_value; 否则,dst（x,y）=0
    cv2.THRESH_BINARY_INV   如果 src(x,y)>threshold, dst(x,y) = 0; 否则,dst(x,y) = max_value
    cv2.THRESH_TRUNC        如果 src(x,y)>threshold, dst(x,y) = max_value; 否则dst(x,y) = src(x,y)
    cv2.THRESH_TOZERO       如果 src(x,y)>threshold, dst(x,y) = src(x,y) ; 否则 dst(x,y) = 0
    cv2.THRESH_TOZERO_INV   如果 src(x,y)>threshold, dst(x,y) = 0 ; 否则dst(x,y) = src(x,y)
    """

    global cur_process_img_index
    cur_process_img_index = process_from
    # scale_cur_img.set(cur_process_img_index)  # 设置初始值

    for i in range(process_from, process_to):
        img_gray = Image.open(gray_images_path[i])
        img_gray_name = get_image_name(gray_images_path[i])

        if binary_type.get() == "THRESH_OTSU":
            type = cv2.THRESH_OTSU
        elif binary_type.get() == "THRESH_OTSU_INV":
            type = cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV
        elif binary_type.get() == "THRESH_BINARY":
            type = cv2.THRESH_BINARY
        elif binary_type.get() == "THRESH_BINARY_INV":
            type = cv2.THRESH_BINARY_INV
        elif binary_type.get() == "THRESH_TRUNC":
            type = cv2.THRESH_TRUNC
        elif binary_type.get() == "THRESH_TOZERO":
            type = cv2.THRESH_TOZERO
        elif binary_type.get() == "THRESH_TOZERO_INV":
            type = cv2.THRESH_TOZERO_INV

        img_binary, img_binary_name, _threshold_value, _ = get_binary_image(
            img_gray,
            img_gray_name,
            thresh=threshold_value.get(),
            type=type,
            save=True)

        # 更新显示窗口
        progressbar_part_binarization['value'] += 1
        binary_threshold_value[i] = _threshold_value

        cur_process_img_index += 1
        # scale_cur_img.set(cur_process_img_index)  # 设置初始值

        update_image_label(gray_label_image, gray_label_text, img_gray,
                           img_gray_name)
        update_image_label(binary_label_image, binary_label_text, img_binary,
                           img_binary_name)

    global binary_images_path, binary_images_count
    binary_images_path, binary_images_count = get_images_path(
        binary_images_dir_path, picture_format.get())

    tkinter.messagebox.showinfo('提示', '范围二值化完成')


button_part_binarization = Button(root,
                                  text="范围二值化",
                                  command=part_binarization)
button_part_binarization.grid(row=1,
                              column=6,
                              columnspan=3,
                              sticky=E + W,
                              padx=3)
button_part_binarization.grid_remove()

progressbar_part_binarization = tkinter.ttk.Progressbar(root)
progressbar_part_binarization.grid(row=0, column=8, sticky=E + W, padx=3)
progressbar_part_binarization.grid_remove()


def batch_generate():
    if binary_images_count == 0:
        tkinter.messagebox.showerror('错误', '请先进行批量二值化!')
        return

    if os.path.exists(output_video_bin_path):  # 如果文件存在
        # 删除文件，可使用以下两种方法。
        os.remove(output_video_bin_path)
        tkinter.messagebox.showinfo("提示", "为避免文件叠加, 已删除旧文件")

    progressbar_generate['maximum'] = binary_images_count

    global cur_process_img_index
    cur_process_img_index = 0
    progressbar_generate['value'] = 0

    for i in range(binary_images_count):
        img_binary = Image.open(binary_images_path[i])
        convert(img_binary, output_video_bin_path, binary_threshold_value[i])

        progressbar_generate['value'] += 1
        root.update()

    tkinter.messagebox.showinfo("提示", "文件生成成功!")


button_generate = Button(root, text="批量转字模", command=batch_generate)
button_generate.grid(row=3, column=3, sticky=E + W)

progressbar_generate = tkinter.ttk.Progressbar(root)
progressbar_generate.grid(row=3, column=4, sticky=E + W, padx=3)

button_batch_grayscale.grid_remove()
button_batch_binarization.grid_remove()
button_generate.grid_remove()
progressbar_batch_binarization.grid_remove()
progressbar_batch_grayscale.grid_remove()
progressbar_generate.grid_remove()


# 一键处理
def simple_process():
    if path.get() == "请选择图片所在文件夹":
        tkinter.messagebox.showerror('错误', '请先选择图片文件夹路径和图片格式!')
        return
    if original_images_count == 0:
        tkinter.messagebox.showerror('错误', '不存在所选格式图片,  请检查图片格式!')
        return

    # 进度值最大值
    progressbar_simple_process['maximum'] = original_images_count
    # 进度值初始值
    progressbar_simple_process['value'] = 0

    if os.path.exists(output_video_bin_path):  # 如果文件存在
        # 删除文件，可使用以下两种方法。
        os.remove(output_video_bin_path)
        tkinter.messagebox.showinfo("提示", "为避免文件叠加, 已删除旧文件")

    for i in original_images_path:
        img = Image.open(i, 'r')
        img = img.resize((128, 64), Image.NEAREST)

        img_name = get_image_name(i)

        # 灰度化
        img_gray, img_gray_name, _ = get_gray_image(img,
                                                    img_name,
                                                    save=gray_save.get())
        # 二值化

        if binary_invert.get():
            type = cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV
        else:
            type = cv2.THRESH_OTSU

        img_binary, img_binary_name, _threshold_value, _ = get_binary_image(
            img_gray, img_gray_name, type=type, save=binary_save.get())

        # 生成图像数组
        convert(img_binary, output_video_bin_path, _threshold_value, False)

        progressbar_simple_process['value'] += 1
        global cur_process_img_index
        cur_process_img_index += 1
        scale_cur_img.set(cur_process_img_index)  # 设置初始值

        update_image_label(origin_label_image, origin_label_text, img,
                           img_name)
        update_image_label(gray_label_image, gray_label_text, img_gray,
                           img_gray_name)
        update_image_label(binary_label_image, binary_label_text, img_binary,
                           img_binary_name)

    tkinter.messagebox.showinfo('提示', '已成功生成bin文件')


button_simple_process = Button(root, text="一键处理", command=simple_process)
button_simple_process.grid(row=4,
                           column=0,
                           pady=6,
                           padx=3,
                           sticky=E + W + N + S)
progressbar_simple_process = tkinter.ttk.Progressbar(root)
progressbar_simple_process.grid(row=4,
                                column=1,
                                rowspan=2,
                                columnspan=2,
                                pady=6,
                                sticky=E + W + N + S,
                                padx=3)


# 二值化反色
def binaryInvertChange():
    print(binary_invert.get())
    process_current_image()


binary_invert = IntVar()
binary_invert.set(False)
checkbutton_binary_invert = Checkbutton(root,
                                        variable=binary_invert,
                                        text="二值化取反",
                                        command=binaryInvertChange)
checkbutton_binary_invert.grid(row=5, column=0, sticky=W)

# 二值化方式
"""
type: 阈值类型
cv2.THRESH_BINARY       如果 src(x,y)>threshold, dst(x,y) = max_value; 否则,dst（x,y）=0
cv2.THRESH_BINARY_INV   如果 src(x,y)>threshold, dst(x,y) = 0; 否则,dst(x,y) = max_value
cv2.THRESH_TRUNC        如果 src(x,y)>threshold, dst(x,y) = max_value; 否则dst(x,y) = src(x,y)
cv2.THRESH_TOZERO       如果 src(x,y)>threshold, dst(x,y) = src(x,y) ; 否则 dst(x,y) = 0
cv2.THRESH_TOZERO_INV   如果 src(x,y)>threshold, dst(x,y) = 0 ; 否则dst(x,y) = src(x,y)
"""
binary_type_list = ('THRESH_OTSU', 'THRESH_OTSU_INV', 'THRESH_BINARY',
                    'THRESH_BINARY_INV', 'THRESH_TRUNC', 'THRESH_TOZERO',
                    'THRESH_TOZERO_INV')
binary_type = StringVar()
binary_type.set(binary_type_list[0])  # 默认设置为bmp


def binary_type_change(selected):
    process_current_image()
    if binary_type.get() == "THRESH_OTSU" or binary_type.get(
    ) == "THRESH_OTSU_INV":
        scale_threshold_value.grid_remove()
    else:
        scale_threshold_value.grid()


optionmenu_binary_type = OptionMenu(root,
                                    binary_type,
                                    *binary_type_list,
                                    command=binary_type_change)
optionmenu_binary_type.grid(row=2,
                            column=6,
                            columnspan=3,
                            sticky=E + W,
                            padx=2)
optionmenu_binary_type.grid_remove()

# scale滚动条，数值从10到40，水平滑动
#tickinterval步进刻度，resolution精度每一步走5
threshold_value = IntVar()


def threshold_value_change(e):
    process_current_image()


scale_threshold_value = Scale(root,
                              from_=0,
                              to=255,
                              orient=HORIZONTAL,
                              resolution=1,
                              variable=threshold_value,
                              width=10,
                              label="二值化阈值:",
                              font=("隶书", 8),
                              sliderlength=20,
                              command=threshold_value_change)
threshold_value.set(127)  # 设置初始值
scale_threshold_value.grid(row=3, column=6, columnspan=3, sticky=E + W + N + S)
scale_threshold_value.grid_remove()


# 保存二值化后的图片
def binary_save_change():
    print(binary_save.get())
    if (binary_save.get()):
        button_binary_save_path.grid()
    else:
        button_binary_save_path.grid_remove()


binary_save = IntVar()
binary_save.set(True)
checkbutton_binary_save = Checkbutton(root,
                                      variable=binary_save,
                                      text="保存二值化图片",
                                      command=binary_save_change)
checkbutton_binary_save.grid(row=5, column=3)


def select_binary_save_path():
    path_ = askdirectory()  #使用askdirectory()方法返回文件夹的路径
    if path_ == "":
        pass
    else:
        path_ = path_.replace("/", "\\")  # 实际在代码中执行的路径为“\“ 所以替换一下
        global binary_images_dir_path
        binary_images_dir_path = path_ + "\\"
        print("二值图保存路径: " + binary_images_dir_path)


button_binary_save_path = Button(root,
                                 text="选择二值图保存路径",
                                 command=select_binary_save_path)
button_binary_save_path.grid(row=5,
                             column=4,
                             pady=6,
                             padx=3,
                             sticky=E + W + N + S)


# 保存灰度化后的图片
def gray_save_change():
    print(gray_save.get())
    if (gray_save.get()):
        button_gray_save_path.grid()
    else:
        button_gray_save_path.grid_remove()


gray_save = IntVar()
gray_save.set(True)
checkbutton_gray_save = Checkbutton(root,
                                    variable=gray_save,
                                    text="保存灰度化图片",
                                    command=gray_save_change)
checkbutton_gray_save.grid(row=4, column=3)


def select_gray_save_path():
    path_ = askdirectory()  #使用askdirectory()方法返回文件夹的路径
    if path_ == "":
        pass
    else:
        path_ = path_.replace("/", "\\")  # 实际在代码中执行的路径为“\“ 所以替换一下
        global gray_images_dir_path
        gray_images_dir_path = path_ + "\\"
        print("灰度图保存路径: " + gray_images_dir_path)


button_gray_save_path = Button(root,
                               text="选择灰度图保存路径",
                               command=select_gray_save_path)
button_gray_save_path.grid(row=4,
                           column=4,
                           pady=6,
                           padx=3,
                           sticky=E + W + N + S)


def process_current_image(save=False):
    if path.get() == "请选择图片所在文件夹":
        tkinter.messagebox.showerror('错误', '请先选择图片文件夹路径和图片格式!')
        return
    if original_images_count == 0:
        tkinter.messagebox.showerror('错误', '不存在所选格式图片,  请检查图片格式!')
        return

    img = Image.open(original_images_path[cur_process_img_index])
    img_name = get_image_name(original_images_path[cur_process_img_index])

    img_gray, img_gray_name, img_gray_save_path = get_gray_image(img,
                                                                 img_name,
                                                                 save=save)

    if binary_type.get() == "THRESH_OTSU":
        type = cv2.THRESH_OTSU
    elif binary_type.get() == "THRESH_OTSU_INV":
        type = cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV
    elif binary_type.get() == "THRESH_BINARY":
        type = cv2.THRESH_BINARY
    elif binary_type.get() == "THRESH_BINARY_INV":
        type = cv2.THRESH_BINARY_INV
    elif binary_type.get() == "THRESH_TRUNC":
        type = cv2.THRESH_TRUNC
    elif binary_type.get() == "THRESH_TOZERO":
        type = cv2.THRESH_TOZERO
    elif binary_type.get() == "THRESH_TOZERO_INV":
        type = cv2.THRESH_TOZERO_INV

    # 简单视图下 勾上 二值化取反 更新图片窗口用到下面4行代码
    if view_choice.get() == "简单":
        if binary_invert.get():
            type = cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV
        else:
            type = cv2.THRESH_OTSU

    img_binary, img_binary_name, _threshold_value, img_binary_save_path = get_binary_image(
        img_gray,
        img_gray_name,
        thresh=threshold_value.get(),
        type=type,
        save=save)

    global cur_img_gray, cur_img_binary, cur_img_binary_threshold_value, cur_img_gray_save_path, cur_img_binary_save_path
    cur_img_gray = img_gray
    cur_img_binary = img_binary
    cur_img_gray_save_path = img_gray_save_path
    cur_img_binary_save_path = img_binary_save_path
    cur_img_binary_threshold_value = _threshold_value

    # 更新显示窗口
    update_image_label(origin_label_image, origin_label_text, img, img_name)
    update_image_label(gray_label_image, gray_label_text, img_gray,
                       img_gray_name)
    update_image_label(binary_label_image, binary_label_text, img_binary,
                       img_binary_name)


def next_pic(*arg):
    if path.get() == "请选择图片所在文件夹":
        tkinter.messagebox.showerror('错误', '请先选择图片文件夹路径和图片格式!')
        return
    if original_images_count == 0:
        tkinter.messagebox.showerror('错误', '不存在所选格式图片,  请检查图片格式!')
        return

    # print(cur_process_img_index)
    global cur_process_img_index
    if cur_process_img_index < original_images_count:
        cur_process_img_index += 1

    scale_cur_img.set(cur_process_img_index)  # 设置初始值
    process_current_image()


def pre_pic(*arg):
    if path.get() == "请选择图片所在文件夹":
        tkinter.messagebox.showerror('错误', '请先选择图片文件夹路径和图片格式!')
        return
    if original_images_count == 0:
        tkinter.messagebox.showerror('错误', '不存在所选格式图片,  请检查图片格式!')
        return

    global cur_process_img_index
    if cur_process_img_index > 0:
        cur_process_img_index -= 1
    # print(cur_process_img_index)
    scale_cur_img.set(cur_process_img_index)  # 设置初始值
    process_current_image()


button_pre_pic = Button(root, text="上一张", command=pre_pic)
button_pre_pic.grid(row=4, column=3, pady=6, sticky=E + W)
button_pre_pic.grid_remove()

button_next_pic = Button(root, text="下一张", command=next_pic)
button_next_pic.grid(row=4, column=4, pady=6, padx=3, sticky=E + W)
button_next_pic.grid_remove()


# 保存当前处理结果
def save_current_process():
    # if (cur_img_gray != None) and (cur_img_gray_save_path != ""):
    #     cur_img_gray.save(cur_img_gray_save_path)
    # if (cur_img_binary != None) and (cur_img_binary_save_path != ""):
    #     cur_img_binary.save(cur_img_binary_save_path)
    process_current_image(save=True)

    with open(output_video_bin_path, "r+b") as f:
        ret = output_image_c_array(cur_img_binary.size[0],
                                   cur_img_binary.size[1],
                                   cur_img_binary.load(),
                                   cur_img_binary_threshold_value, False)

        print(f.tell())
        f.seek(int(cur_process_img_index * 128 * 64 / 8))
        print(f.tell())

        f.write(bytearray(ret))  # 自带文件关闭功能，不需要再写f.close()


button_cur_binary = Button(root, text="更新当前帧", command=save_current_process)
button_cur_binary.grid(row=4, column=5, pady=6, padx=2, sticky=E + W + N + S)
button_cur_binary.grid_remove()


def cur_img_change(e):
    global cur_process_img_index
    cur_process_img_index = scale_cur_img.get()
    process_current_image()


scale_cur_img = Scale(root,
                      from_=0,
                      to=original_images_count,
                      orient=HORIZONTAL,
                      resolution=1,
                      width=10,
                      sliderlength=20,
                      command=cur_img_change)
scale_cur_img.grid(row=4, column=0, columnspan=3, sticky=E + W + N + S)
scale_cur_img.grid_remove()


#创建一个下拉式菜单
#执行[文件/新建]菜单命令，显示一个对话框
def doFileNewCommand(*arg):
    tkinter.messagebox.askokcancel("菜单", "你正在选择“新建”菜单命令")


#执行[文件/打开]菜单命令，显示一一个对话框
def doFileOpenCommand(*arg):
    tkinter.messagebox.askokcancel("菜单", "你正在选择“打开”菜单命令")


#执行[文件/保存]菜单命令，显示-一个对话框
def doFileSaveCommand(*arg):
    tkinter.messagebox.askokcancel("菜单", "你正在选择“文档”菜单命令")


#执行[帮助/档]菜单命令,显示一个对话框
def doHelpContentsCommand(*arg):
    tkinter.messagebox.askokcancel("菜单", "你正在选择“保存”菜单命令")


#执行[帮助/文关于]菜单命令，显示一个对话框
def doHelpAboutCommand(*arg):
    tkinter.messagebox.showinfo("提示", "作者: 十萬九千七")


def view_choice_change(*arg):
    if view_choice.get() == "简单":
        optionmenu_binary_type.grid_remove()
        checkbutton_binary_invert.grid()
        button_simple_process.grid()
        progressbar_simple_process.grid()
        button_batch_grayscale.grid_remove()
        button_batch_binarization.grid_remove()
        button_generate.grid_remove()
        progressbar_batch_binarization.grid_remove()
        progressbar_batch_grayscale.grid_remove()
        progressbar_generate.grid_remove()

        button_gray_save_path.grid(row=4,
                                   column=4,
                                   pady=6,
                                   padx=3,
                                   sticky=E + W + N + S)
        button_binary_save_path.grid(row=5,
                                     column=4,
                                     pady=6,
                                     padx=3,
                                     sticky=E + W + N + S)
        checkbutton_gray_save.grid()
        checkbutton_binary_save.grid()
        scale_threshold_value.grid_remove()

        button_pre_pic.grid_remove()
        button_next_pic.grid_remove()

        root.unbind("<KeyPress-Left>")
        root.unbind("<KeyPress-Right>")

        button_cur_binary.grid_remove()
        scale_cur_img.grid_remove()

        entry_part_binarization_from.grid_remove()
        entry_part_binarization_to.grid_remove()

        button_part_binarization.grid_remove()
        progressbar_part_binarization.grid_remove()

    elif view_choice.get() == "高级":
        checkbutton_binary_invert.grid_remove()
        button_simple_process.grid_remove()
        progressbar_simple_process.grid_remove()
        optionmenu_binary_type.grid()
        button_batch_grayscale.grid()
        button_batch_binarization.grid()
        button_generate.grid()
        progressbar_batch_binarization.grid()
        progressbar_batch_grayscale.grid()
        progressbar_generate.grid()

        button_gray_save_path.grid(row=1,
                                   column=5,
                                   pady=6,
                                   padx=3,
                                   sticky=E + W + N + S)
        button_binary_save_path.grid(row=2,
                                     column=5,
                                     pady=6,
                                     padx=3,
                                     sticky=E + W + N + S)

        checkbutton_gray_save.grid_remove()
        checkbutton_binary_save.grid_remove()

        button_part_binarization.grid()
        progressbar_part_binarization.grid()

        button_pre_pic.grid()
        button_next_pic.grid()

        root.bind("<KeyPress-Left>", pre_pic)
        root.bind("<KeyPress-Right>", next_pic)

        button_cur_binary.grid()
        scale_cur_img.grid()

        entry_part_binarization_from.grid()
        entry_part_binarization_to.grid()


#创建-一个下拉式菜单(pull-down)
mainmenu = Menu(root)
#新增"文件"菜单的子菜单
filemenu = Menu(mainmenu, tearoff=0)
#新增"文件"菜单的菜单项
filemenu.add_command(label="退出", command=root.quit)
#新增"文件"菜单
mainmenu.add_cascade(label="文件", menu=filemenu)

#新增"视图"菜单的子菜单
viewmenu = Menu(mainmenu, tearoff=0)
#新增"视图"菜单的菜单项
view_choice = StringVar()
view_choice.set("简单")
viewmenu.add_radiobutton(label="简单",
                         command=view_choice_change,
                         variable=view_choice,
                         value="简单")
viewmenu.add_radiobutton(label="高级",
                         command=view_choice_change,
                         variable=view_choice,
                         value="高级")
#新增"帮助"菜单
mainmenu.add_cascade(label="视图", menu=viewmenu)

#新增"帮助"菜单的子菜单
helpmenu = Menu(mainmenu, tearoff=0)
#新增"帮助"菜单的菜单项
helpmenu.add_command(label="文档",
                     command=doHelpContentsCommand,
                     accelerator="F1")
helpmenu.add_command(label="关于",
                     command=doHelpAboutCommand,
                     accelerator="Ctrl+A")
#新增"帮助"菜单
mainmenu.add_cascade(label="帮助", menu=helpmenu)

#设置主窗口的菜单
root.config(menu=mainmenu)
root.bind("<Control-n>", doFileNewCommand)
root.bind("<Control-N>", doFileNewCommand)
root.bind("<Control-o>", doFileOpenCommand)
root.bind("<Control-O>", doFileOpenCommand)
root.bind("<Control-s>", doFileSaveCommand)
root.bind("<Control-S>", doFileSaveCommand)
root.bind("<F1>", doHelpContentsCommand)
root.bind("<Control-a>", doHelpAboutCommand)
root.bind("<Control-A>", doHelpAboutCommand)

#开始程序循环
root.mainloop()
