import os
import json
import argparse

import commonVar

parser = argparse.ArgumentParser(description="Deploy script for subgames.")
parser.add_argument(
    "--type",
    "-t",
    required=True,
    choices=["s", "f", "r"],
    help="Type of game to deploy: 's' for wlzb, 'f' for lxby, 'r' for wlzbtest.",
)
args = parser.parse_args()

# 映射参数到游戏类型
game_type_mapping = {"s": "wlzb", "f": "lxby", "r": "wlzb/wlzbtest"}
game_type = game_type_mapping[args.type]

if game_type == "wlzb":
    VERSION_PATH = "/Users/lishan/Work/project/slot/allConfig/BVersion.json"
    GAME_HTML_PATH = "/Users/lishan/Work/project/slot/allConfig/index.html"
    BASE_URL = "https://wlzb.fish333.com/"
    TITLE = "5LIONS"
    START_SCENE = "c1bc28a2-729f-47d8-81bc-cbf91d2e4944"
elif game_type == "lxby":
    VERSION_PATH = "/Users/lishan/Work/project/ljfish/allConfig/BVersion.json"
    GAME_HTML_PATH = "/Users/lishan/Work/project/ljfish/allConfig/index.html"
    BASE_URL = "https://lxby.fish333.com/"
    TITLE = "FISH"
    START_SCENE = "1ef1c33a-a268-466b-b72b-9bf22b36cf2d"
else:
    print("游戏未配置")
    exit(0)

IS_DEBUG = "false"
IS_CONSOLE = "false"

# 检查并处理版本文件
if not os.path.isfile(VERSION_PATH):
    with open(VERSION_PATH, "w") as f:
        json.dump({"version": 1}, f)
    print("json文件创建完成")
    nv = 1
else:
    with open(VERSION_PATH, "r") as f:
        version_data = json.load(f)
    nv = version_data.get("version", 0) + 1
    with open(VERSION_PATH, "w") as f:
        json.dump({"version": nv}, f)

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

commonVar.clean_build_directory(commonVar.BUILD_PATH)

TO_BUILD_PATH = commonVar.create_version_directory(commonVar.BUILD_PATH, nv)

# 执行命令行命令
cmd = (
    f"{commonVar.CCC_PATH2} --path {commonVar.PROJECT_PATH} "
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
    commonVar.run_python_script("./buildZip.py", "-t", f"{args.type}")
else:
    print(f"构建失败，返回码：{return_code}")
