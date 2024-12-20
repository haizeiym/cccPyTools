import os
import json
import argparse

import commonVar

parser = argparse.ArgumentParser(description="Deploy script for subgames.")
parser.add_argument(
    "--type",
    "-t",
    required=True,
    choices=["w", "l", "ww"],
    help="Type of game to deploy: 'w' for wlzb, 'l' for lxby, 'ww' for wlzbtest.",
)
args = parser.parse_args()

# 映射参数到游戏类型
game_type_mapping = {"w": "wlzb", "l": "lxby", "ww": "wlzb/wlzbtest"}
game_type = game_type_mapping[args.type]

if game_type == "wlzb":
    PROJECT_PATH = "/Users/lishan/Work/project/slot"
    BUILD_PATH = "/Users/lishan/Work/project/slot/build"
    VERSION_PATH = "config/wlzb/BVersion.json"
    GAME_HTML_PATH = "config/wlzb/index.html"

    BASE_URL = "https://wlzb.fish333.com/"

    TITLE = "5LIONS"
    START_SCENE = "c1bc28a2-729f-47d8-81bc-cbf91d2e4944"
elif game_type == "lxby":
    PROJECT_PATH = "/Users/lishan/Work/project/ljfish"
    BUILD_PATH = "/Users/lishan/Work/project/ljfish/build"
    VERSION_PATH = "config/lxby/BVersion.json"
    GAME_HTML_PATH = "config/lxby/index.html"

    BASE_URL = "https://lxby.fish333.com/"

    TITLE = "FISH"
    START_SCENE = "1ef1c33a-a268-466b-b72b-9bf22b36cf2d"
else:
    print("游戏未配置")
    exit(0)

IS_DEBUG = "false"
IS_CONSOLE = "false"

# 检查并处理版本文件
try:
    # 确保目录存在
    os.makedirs(os.path.dirname(VERSION_PATH), exist_ok=True)

    # 读取版本号
    try:
        with open(VERSION_PATH, "r") as f:
            version_data = json.load(f)
            nv = version_data.get("version", 0) + 1
    except FileNotFoundError:
        # 文件不存在时创建新文件
        nv = 1
        print("json文件创建完成")

    # 写入新版本号
    with open(VERSION_PATH, "w") as f:
        json.dump({"version": nv}, f)

except Exception as e:
    print(f"处理版本文件时出错: {e}")
    exit(1)

# 构建游戏链接
GAME_URL = f"{BASE_URL}v{nv}/web-mobile/index.html"

# 构建 HTML 内容
HTTP_HEAD = """
    <head>
        <meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate" />
        <meta http-equiv="pragma" content="no-cache" />
        <meta http-equiv="Expires" content="0" />
    </head>
"""

HTTP_BODY = f"""
    <body>
        <script>
            var search = window.location.search;
            window.location.href = `{GAME_URL}${{search}}`;
        </script>
    </body>
"""

INPUT = f"<!DOCTYPE html>\n<html>\n{HTTP_HEAD}\n{HTTP_BODY}\n</html>"

# 检查并处理 HTML 文件
if not os.path.isfile(GAME_HTML_PATH):
    with open(GAME_HTML_PATH, "w") as f:
        f.write(INPUT)
    print("index文件创建完成")
else:
    with open(GAME_HTML_PATH, "w") as f:
        f.write(INPUT)

commonVar.clean_build_directory(BUILD_PATH)

TO_BUILD_PATH = commonVar.create_version_directory(BUILD_PATH, nv)

# 执行命令行命令
cmd = (
    f"{commonVar.CCC_PATH2} --path {PROJECT_PATH} "
    f'--build "platform=web-mobile;'
    f"title={TITLE};"
    f"debug={IS_DEBUG};"
    f"embedWebDebugger={IS_CONSOLE};"
    f"startScene={START_SCENE};"
    f"webOrientation=landscape;"
    f"buildPath={TO_BUILD_PATH};"
    f'md5Cache=true;"'
)

return_code = commonVar.run_command(cmd)

# 检查构建是否成功
if return_code == 0:
    print("构建成功完成，执行图片压缩")
    commonVar.optimize_pngs(f"{TO_BUILD_PATH}/web-mobile")
    print("图片压缩完成，执行打包")
    commonVar.run_python_script(
        "./buildZip.py", "-t", f"{game_type}", "-p", f"{BUILD_PATH}"
    )
else:
    print(f"构建失败，返回码：{return_code}")
