import os
import subprocess
import argparse

import commonVar


def main():
    # 设置参数
    parser = argparse.ArgumentParser(description="Deploy script for subgames.")
    parser.add_argument(
        "--type",
        "-t",
        required=True,
        choices=["wlzb", "lxby", "wlzbtest"],
    )
    parser.add_argument(
        "--path",
        "-p",
        required=True,
        help="压缩路径",
    )

    args = parser.parse_args()

    # 映射参数到游戏类型
    game_type = f"{args.type}"

    bzip_path = f"{args.path}"
    fzip_name = next((f for f in os.listdir(bzip_path) if f.startswith("v")), None)
    if not fzip_name:
        print("No file starting with 'v' found in build directory.")
        return

    zip_name = f"{fzip_name}.tar.gz"
    out_zip_name = os.path.join(bzip_path, zip_name)

    # 压缩命令
    try:
        subprocess.run(
            ["tar", "-zcvf", out_zip_name, "-C", bzip_path, fzip_name], check=True
        )
        print(f"Compressed to: {out_zip_name}")
    except subprocess.CalledProcessError as e:
        print(f"Compression failed: {e}")
        return

    # 远程服务器信息
    hostname = "34.92.21.24"
    username = "keno"
    bast_remote_path = "/www/wwwroot/subgame/"
    remote_path = os.path.join(bast_remote_path, game_type)

    private_key_path = "/Users/lishan/Work/server/ssh/key/keno"

    # 建立 SSH 连接
    ssh = None
    sftp = None
    try:
        ssh = commonVar.create_ssh_connection(hostname, username, private_key_path)
        sftp = ssh.open_sftp()

        # 上传压缩文件并显示进度
        commonVar.upload_file_with_progress(
            sftp, out_zip_name, os.path.join(remote_path, zip_name)
        )

        # 解压和查看文件
        ssh_command = f"cd {remote_path} && tar -zxvf {zip_name} && ls"
        stdin, stdout, stderr = ssh.exec_command(ssh_command)
        stdout.channel.recv_exit_status()
        result, error = stdout.read().decode("utf-8"), stderr.read().decode("utf-8")
        print("Result:", result)
        if error:
            print("Error:", error)

        # 上传 index.html 并显示进度
        index_path = os.path.join(
            os.path.dirname(__file__), f"config/{game_type}/index.html"
        )
        commonVar.upload_file_with_progress(
            sftp, index_path, os.path.join(remote_path, "index.html")
        )
    except Exception as e:
        print(f"Operation failed: {e}")
    finally:
        if sftp:
            sftp.close()
        if ssh:
            ssh.close()
        print("SSH connection closed.")


if __name__ == "__main__":
    main()
