import argparse
from .version import __version__


def main() -> None:
    parser = argparse.ArgumentParser(prog="pyzpacker")
    parser.add_argument("source", type=str, help="要打包的模块")
    parser.add_argument("-o", "--output", type=str, help="打包完成后放到哪里")
    parser.add_argument("-m", "--main", type=str, help="指定入口函数,形式为`module[.module.module...]:function`")
    parser.add_argument("-r", "--with-requirements", type=str, help="指定requirements.txt文件并安装其中的依赖到包中")
    parser.add_argument("-c", "--compress", action='store_false', help="是否压缩")
    parser.add_argument("-i", "--with-interpreter", action='store_false', help="是否加入`/usr/bin/env python3`作为`Shebang`")
    parser.add_argument("-p", "--with-compile", action='store_false', help="是否仅将编译好的字节码作打包")
    parser.add_argument("-v", "--version", help="查看pyzpacker版本号",
                        action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()
    
