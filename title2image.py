# https://www.ruanx.net/auto-blog-banner/
from flask import Flask, request, jsonify, send_file,render_template
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import io
import textwrap

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def download_image(url, save_path):
    """
    下载图片并保存到本地文件

    Args:
        url (str): 图片的URL地址
        save_path (str): 保存图片的文件路径

    Returns:
        bool: 下载成功返回True，否则返回False
    """
    response = requests.get(url)
    if response.status_code == 200:
        image_data = response.content
        with open(save_path, 'wb') as f:
            f.write(image_data)
        return True
    else:
        return False



def generate_image(image_path, title, output_path, font_path, max_line_size, text_color=(255, 255, 255), mask_color=(0, 0, 0, 30), blur_radius=5, offset_y=0):
    """
    生成带有标题文本的图片，并添加蒙板和高斯模糊

    Args:
        image_path (str): 输入图片文件路径
        title (str): 标题文本
        output_path (str): 生成图片的文件路径
        font_path (str): 字体文件路径
        max_line_size (int): 每行的最大字符数
        text_color (tuple): 文本颜色，默认为白色
    Returns:
        None
    """
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    image_width, image_height = image.size
    text_width = (6 / 7) * image_width
    max_line_size = int(max_line_size)
    offset_y = int(offset_y)

    # 设置字体大小，计算每行的最大宽度和高度
    font_size = int(text_width / max_line_size)
    font = ImageFont.truetype(font_path, font_size)

    # 对标题进行换行处理
    text_lines = textwrap.wrap(title, max_line_size)

    # 计算文本总高度，使用 getbbox 计算单行文本的高度
    line_height = font.getbbox('A')[3] - font.getbbox('A')[1]+20  # 获取字符 'A' 的上下边界，得出高度
    total_text_height = line_height * len(text_lines)

    # 起始位置 (x, y)，使文本垂直居中
    text_x = image_width / 2
    text_y = (image_height - total_text_height) / 2 - offset_y

    # 绘制文本，逐行进行居中对齐
    for line in text_lines:
        # 使用 textbbox 代替 textsize 来获取文本边界框
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        
        # 绘制文本并水平居中
        draw.text((text_x - line_width / 2, text_y), line, fill=text_color, font=font)
        text_y += line_height

    # 保存生成的图片
    image.save(output_path, "PNG")
    image.close()



@app.route('/generate_image', methods=['GET'])
def generate_image_api():
    title = request.args.get('title')
    max_line_size = request.args.get('max_line_size', 15)  # 获取max_line_size参数，默认为6
    offset_y = request.args.get('offset_y', 50)  # 获取max_line_size参数，默认为6
    # 调用下载函数
    # image_url = "https://t.mwm.moe/fj/"
    # download_success = download_image(image_url, "your_image.jpg")

    # if download_success:
    # 调用生成图片函数
    image_path = "your_image.jpg"
    output_image_path = f"{title}.png"  # 注意保存为 PNG 格式，以支持透明度
    font_path = "HYZY.otf"
    generate_image(image_path, title, output_image_path, font_path, max_line_size,offset_y=offset_y)
    # 返回生成的图片
    return send_file(output_image_path, as_attachment=True)
    # else:
    #     return jsonify({'message': '无法下载图片'})


if __name__ == '__main__':
    app.run(debug=True,port=5000,host='0.0.0.0')
