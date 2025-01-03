import os
from PIL import Image
import io
import base64
from openai import OpenAI

def encode_image(image_path, max_size=(40, 40)):
    """压缩并编码图片"""
    # 打开并压缩图片
    with Image.open(image_path) as img:
        # 转换为RGB模式（去除透明通道）
        if img.mode in ('RGBA', 'P'): 
            img = img.convert('RGB')
        # 等比例缩放
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        # 转换为JPEG格式（压缩率更高）
        buffer = io.BytesIO()
        img.save(buffer, format=img.format)  # 使用原始格式
        #img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

# def encode_image(image_path):
#     """
#     读取本地图像文件并编码为BASE64格式。

#     参数:
#         image_path (str): 图像文件的路径。

#     返回:
#         str: 编码后的BASE64字符串。
#     """
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode("utf-8")


    
def analyze_image_with_deepseek(image_path, prompt, rules):
    """
    使用 deepseek API 分析图像并获取结果。

    参数:
        image_path (str): 图像文件的路径。
        prompt (str): 分析提示词。
        rules (str): 分析规则。

    返回:
        str: deepseek API 的分析结果。
    """
    # 初始化 OpenAI 客户端，使用 deepseek 的 API key 和 base URL
    client = OpenAI(
        api_key="",
        base_url="https://api.deepseek.com",
    )
    # 将图像文件编码为BASE64格式
    base64_image = encode_image(image_path)
    # 打印BASE64字符串长度，用于调试和性能分析
    print(f"图片Base64字符串长度: {len(base64_image)}")
    # 通过文件名后缀获取图像格式，并将其转换为小写
    image_format = image_path.split('.')[-1].lower()
    # 构建 image_url 参数，用于在请求中传递图像数据
    image_url = f"data:image/{image_format};base64,{base64_image}"
    # 尝试创建聊天完成以分析图像
    try:
        completion = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", 
                         "text": f"{prompt}\n{rules}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": image_url}
                        }
                    ]
                }
            ],
            stream=False
        )
        # 返回分析结果的JSON表示
        return completion.model_dump_json()
    except Exception as e:
        # 如果发生异常，打印错误信息并返回错误消息的字符串表示
        print(f"Error analyzing image {image_path}: {e}")
        return str(e)