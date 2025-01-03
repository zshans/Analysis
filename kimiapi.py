from pathlib import Path
from openai import OpenAI


# client = OpenAI(
#     api_key = "",
#     base_url = "https://api.moonshot.cn/v1",
# )
 
# model_list = client.models.list()
# model_data = model_list.data
 
# for i, model in enumerate(model_data):
#     print(f"model[{i}]:", model.id)


def analyze_image_with_kimi(image_path, prompt, rules):
    """
    使用 Kimi API 分析图像并获取结果。

    参数:
        image_path (str): 图像文件的路径。
        prompt (str): 分析提示词。
        rules (str): 分析规则。

    返回:
        str: Kimi API 的分析结果。
    """
    client = OpenAI(
        api_key = "",
        base_url = "https://api.moonshot.cn/v1",
    )

    # 上传图像文件
    # xlnet.pdf 是一个示例文件, 我们支持 pdf, doc 以及图片等格式, 对于图片和 pdf 文件，提供 ocr 相关能力
    file_object = client.files.create(file=Path(image_path), purpose="file-extract")
    
    # 获取文件内容
    # 获取结果
    # file_content = client.files.retrieve_content(file_id=file_object.id)
    # 注意，之前 retrieve_content api 在最新版本标记了 warning, 可以用下面这行代替
    # 如果是旧版本，可以用 retrieve_content
    file_content = client.files.content(file_id=file_object.id).text
    
    # 构建消息列表
    messages = [
        {
            "role": "system",
            "content": rules,
        },
        {
            "role": "system",
            "content": file_content,
        },
        {"role": "user", "content": prompt},
    ]
    
    # 调用 chat-completion 获取回复
    completion = client.chat.completions.create(
        model="moonshot-v1-auto",
        messages=messages,
        temperature=0.3,
    )
    return completion.choices[0].message
