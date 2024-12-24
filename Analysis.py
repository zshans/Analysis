import os
import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser

def read_config(file_path):
    """
    读取配置文件并返回一个 ConfigParser 对象。

    参数:
        file_path (str): 配置文件的路径。

    返回:
        configparser.ConfigParser: 包含配置数据的 ConfigParser 对象。
    """
    config = configparser.ConfigParser()
    # 检查配置文件是否存在
    if os.path.exists(file_path):
        # 读取配置文件，指定编码为 utf-8
        config.read(file_path, encoding='utf-8')
    else:
        # 如果文件不存在，打印错误信息
        print(f"配置文件 {file_path} 未找到。")
    return config

def analyze_image(image_path, config):
    """
    分析图像文件并返回分析结果。

    参数:
        image_path (str): 图像文件的路径。
        config (configparser.ConfigParser): 包含分析提示和规则的配置对象。
    
    返回:
        str: 分析结果字符串。
    """
    # 从配置对象中获取分析提示词，如果不存在则使用默认提示词
    prompt = config['Analysis'].get('Prompt', '默认提示词')
    # 从配置对象中获取分析规则，如果不存在则使用默认规则
    rules = config['Analysis'].get('Rules', '默认规则')
    # 获取当前时间并格式化
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    # 构建分析结果字符串，包含时间
    analysis_result = f"{current_time} - 分析使用提示词：{prompt} 和规则：{rules}"
    return analysis_result

log_lock = threading.Lock()

def log_result(folder_path, result):
    """
    将分析结果记录到日志文件中。

    参数:
        folder_path (str): 图像文件所在文件夹的路径。
        result (str): 分析结果字符串。
    """
    # 构建日志文件的路径，将文件夹路径与日志文件名连接起来
    log_file_path = os.path.join(folder_path, 'log.txt')
    # 使用互斥锁确保线程安全地写入日志文件
    with log_lock:
        # 打开日志文件，如果不存在则创建，以追加模式写入
        with open(log_file_path, 'a', encoding='utf-8') as file:
            # 将分析结果写入日志文件，并添加换行符
            file.write(f"{result}\n")
            
class ImageUpdateHandler(FileSystemEventHandler):
    def __init__(self, main_folder, config):
        """
        初始化 ImageUpdateHandler 类。

        参数:
            main_folder (str): 要监控的主文件夹路径。
            config (configparser.ConfigParser): 包含分析提示和规则的配置对象。
        """
        # 设置要监控的主文件夹路径
        self.main_folder = main_folder
        # 设置配置对象
        self.config = config
        # 创建一个集合，用于记录已处理的文件路径
        self.processed_files = set()
        # 创建一个字典，用于记录最近修改的文件及其时间戳
        self.recently_modified_files = {}

    def on_modified(self, event):
        """
        处理文件修改事件。

        参数:
            event (FileSystemEvent): 表示文件系统事件的对象。

        该方法执行以下步骤：
        1. 检查事件是否为文件修改事件且不是目录修改事件。
        2. 获取修改文件的路径。
        3. 检查文件是否为图像文件（.png, .jpg, .jpeg, .bmp, .gif）。
        4. 获取文件所在的文件夹路径。
        5. 检查文件是否已处理过。
        6. 如果文件未处理过，检查文件是否在最近修改的文件列表中，或者距离上次修改已经超过0.1秒。
        7. 如果文件满足条件，将文件标记为已处理，并启动一个新线程来处理该文件。
        """
        # 检查事件是否为文件修改事件且不是目录修改事件
        if not event.is_directory and event.event_type == 'modified':
            # 获取修改文件的路径
            file_path = event.src_path
            # 检查文件是否为图像文件（.png, .jpg, .jpeg, .bmp, .gif）
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                folder_path = os.path.dirname(file_path) # 获取文件所在的文件夹路径
                #if file_path not in self.processed_files:  # 检查文件是否已处理
                current_time = time.time()
                # 检查文件是否在最近修改的文件列表中，或者距离上次修改已经超过5秒
                if file_path not in self.recently_modified_files or current_time - self.recently_modified_files[file_path] > 5:
                    # 如果文件不在最近修改的文件列表中，或者距离上次修改已经超过5秒
                    self.recently_modified_files[file_path] = current_time
                    #self.processed_files.add(file_path)  # 标记文件为已处理
                    # 启动一个新线程来处理该文件
                    threading.Thread(target=self.process_image, args=(file_path, folder_path)).start()

    def process_image(self, image_path, folder_path):
        """
        处理图像文件的函数。

        参数:
            image_path (str): 图像文件的路径。
            folder_path (str): 图像文件所在文件夹的路径。

        该函数执行以下步骤：
        1. 打印正在处理的图像文件路径。
        2. 调用 analyze_image 函数分析图像文件，并获取分析结果。
        3. 调用 log_result 函数将分析结果记录到日志文件中。
        4. 打印线程信息和分析结果。
        """
        
        result = analyze_image(image_path, self.config)
        log_result(folder_path, result)
        print(f"线程 {threading.current_thread().ident} 已处理 {image_path}：{result}")

def main():
    """
    主函数，负责启动图像分析监控程序。

    该函数执行以下步骤：
    1. 设置要监控的主文件夹路径。
    2. 构建配置文件的路径，将主文件夹路径与配置文件名连接起来。
    3. 调用 read_config 函数读取配置文件，并返回一个 ConfigParser 对象。
    4. 创建一个 ImageUpdateHandler 实例，传入主文件夹路径和配置对象作为参数。
    5. 创建一个 Observer 实例，并使用 schedule 方法将事件处理器与主文件夹关联起来。
    6. 启动 Observer 实例，开始监控文件系统事件。
    7. 进入一个无限循环，每隔5秒检查一次，直到接收到 KeyboardInterrupt 异常。
    8. 停止 Observer 实例，并等待所有线程完成。
    """
    # 设置要监控的主文件夹路径为 'data'
    main_folder = 'data'
    # 构建配置文件的路径，将主文件夹路径与配置文件名 'Analysis_Template.ini' 连接起来
    config_file_path = os.path.join(main_folder, 'Analysis_Template.ini')
    # 调用 read_config 函数读取配置文件，并返回一个 ConfigParser 对象
    config = read_config(config_file_path)
    
    # 创建一个 ImageUpdateHandler 实例，传入主文件夹路径和配置对象作为参数
    event_handler = ImageUpdateHandler(main_folder, config)
    # 创建一个 Observer 实例
    observer = Observer()
    # 使用 schedule 方法将事件处理器与主文件夹关联起来，并设置递归监控
    observer.schedule(event_handler, main_folder, recursive=True)
    # 启动 Observer 实例，开始监控文件系统事件
    observer.start()
    
    try:
        # 进入一个无限循环，每隔5秒检查一次，直到接收到 KeyboardInterrupt 异常
        while True:
            time.sleep(5)  # 每5秒检查一次
    except KeyboardInterrupt:
        # 接收到 KeyboardInterrupt 异常时，停止 Observer 实例
        observer.stop()
    # 等待所有线程完成
    observer.join()

if __name__ == "__main__":
    main()

