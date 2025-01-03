import os
import base64  # 导入 base64 模块
from openai import OpenAI


def encode_image(image_path):
    """
    读取本地图像文件并编码为BASE64格式。

    参数:
        image_path (str): 图像文件的路径。

    返回:
        str: 编码后的BASE64字符串。
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def analyze_image_with_qwen2_5(image_path, prompt, rules):
    """
    使用 qwen2.5 API 分析图像并获取结果。

    参数:
        image_path (str): 图像文件的路径。
        prompt (str): 分析提示词。
        rules (str): 分析规则。

    返回:
        str: qwen2.5 API 的分析结果。
    """
    client = OpenAI(
        api_key="",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )
    base64_image = encode_image(image_path)  # 编码图像文件为BASE64格式
    print(f"图片Base64字符串长度: {len(base64_image)}")
    image_format = image_path.split('.')[-1].lower()  # 获取图像格式
    image_url = f"data:image/{image_format};base64,{base64_image}"  # 构建 image_url 参数
    try:
        completion = client.chat.completions.create(
            model="qwen-vl-plus",
            messages=[{"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "text", "text": rules},
                {"type": "image_url", "image_url": {"url": image_url}}
            ]}]
        )
        return completion.model_dump_json()
    except Exception as e:
        print(f"Error analyzing image {image_path}: {e}")
        return str(e)