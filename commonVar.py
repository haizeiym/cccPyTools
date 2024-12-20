import os
import sys
import subprocess
import shutil

import paramiko
from paramiko import RSAKey


from stat import S_ISDIR

CCC_PATH2 = (
    "/Applications/Cocos/Creator/2.4.13/CocosCreator.app/Contents/MacOS/CocosCreator"
)

PROJECT_PATH = "/Users/lishan/Work/project/slot"
BUILD_PATH = "/Users/lishan/Work/project/slot/build"

PNGQUANT = "/opt/homebrew/bin/pngquant"


def run_python_script(script_path, *args):
    cmd = [sys.executable, script_path] + list(args)
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())

    return process.poll()


def run_command(cmd):
    # 创建进程
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )

    # 实时读取输出
    while True:
        output = process.stdout.readline()
        if output == "" and process.poll() is not None:
            break
        if output:
            print(output.strip())
            sys.stdout.flush()  # 确保输出立即显示

    # 获取返回码
    return_code = process.poll()
    return return_code


def create_ssh_connection(hostname, username, private_key_path, port=22):
    """
    创建一个 SSH 连接，直接加载私钥文件。

    :param hostname: 远程主机地址
    :param username: 用户名
    :param private_key_path: 私钥路径
    :param port: SSH 端口
    :return: 一个已连接的 paramiko SSHClient 实例
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 加载私钥
        private_key = RSAKey.from_private_key_file(private_key_path)
        ssh.connect(hostname, port=port, username=username, pkey=private_key)
        print("SSH connection established.")
        return ssh
    except Exception as e:
        print(f"Failed to connect via SSH: {e}")
        raise


def upload_file_with_progress(sftp, local_path, remote_path):
    """
    使用 SFTP 上传文件并显示进度。

    :param sftp: 已连接的 SFTPClient 实例
    :param local_path: 本地文件路径
    :param remote_path: 远程文件路径
    """
    file_size = os.path.getsize(local_path)
    progress = 0

    def progress_callback(transferred, total):
        nonlocal progress
        progress = transferred
        percentage = (transferred / total) * 100
        print(
            f"\rUploading {local_path} to {remote_path}: {percentage:.2f}% ({transferred}/{total} bytes)",
            end="",
        )

    try:
        sftp.put(local_path, remote_path, callback=progress_callback)
        print(f"\nUpload of {local_path} completed.")
    except Exception as e:
        print(f"\nFailed to upload {local_path}: {e}")
        raise


def clean_build_directory(build_path):
    """
    清空构建目录
    :param build_path: 构建目录的路径
    """
    if not os.path.exists(build_path):
        print(f"构建目录不存在: {build_path}")
        return

    try:
        # 切换到构建目录
        original_dir = os.getcwd()
        os.chdir(build_path)
        print(f"已切换到目录: {build_path}")

        # 列出目录中的所有项目
        items = os.listdir(build_path)

        if not items:
            print("构建目录已经是空的")
            return

        # 删除目录中的所有项目
        for item in items:
            item_path = os.path.join(build_path, item)
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
                print(f"已删除文件: {item}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"已删除目录: {item}")

        print("构建目录已清空")

    except Exception as e:
        print(f"清空目录时发生错误: {e}")

    finally:
        # 切回原始目录
        os.chdir(original_dir)
        print(f"已切回原始目录: {original_dir}")


def create_version_directory(build_path, version):
    """
    创建版本目录
    :param build_path: 构建目录的路径
    :param version: 版本号
    :return: 创建的版本目录路径
    """
    # 构造版本目录路径
    version_dir = os.path.join(build_path, f"v{version}")

    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(version_dir):
        try:
            os.makedirs(version_dir)
            print(f"已创建版本目录: {version_dir}")
        except OSError as e:
            print(f"创建版本目录时发生错误: {e}")
            return None
    else:
        print(f"版本目录已存在: {version_dir}")

    return version_dir


def optimize_pngs(init_path, quality=65):
    # 查找所有PNG文件
    png_files = []
    for root, dirs, files in os.walk(init_path):
        png_files.extend(
            [
                os.path.join(root, file)
                for file in files
                if file.lower().endswith(".png") or file.lower().endswith(".jpg")
            ]
        )

    # 检查是否找到PNG文件
    if not png_files:
        print(f"在 {init_path} 中没有找到PNG文件")
        return

    # 处理每个PNG文件
    for file in png_files:
        try:
            res_code = run_command(
                f"{PNGQUANT} --skip-if-larger --force --quality={quality} --verbose --output {file} {file}"
            )
            if res_code == 0:
                print(f"成功优化: {file}")
            else:
                print(f"优化失败 {file}")
        except subprocess.CalledProcessError as e:
            print(f"优化失败 {file}: {e.stderr.decode()}")
