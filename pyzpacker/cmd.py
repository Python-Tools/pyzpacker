import argparse
from .version import __version__
from .pyzpacker import pyzpacker


def main() -> None:
    parser = argparse.ArgumentParser(prog="pyzpacker")
    parser.add_argument("source", type=str, help="要打包的模块")
    parser.add_argument("-o", "--output", type=str, help="打包完成后放到哪里")
    parser.add_argument("-m", "--main", type=str, required=True,
                        help="指定入口函数,形式为`module[.module.module...]:function`")
    parser.add_argument("-r", "--with-requirements", type=str,
                        help="指定requirements.txt文件并安装其中的依赖到包中")
    parser.add_argument("-c", "--with_compress", action='store_true', help="是否压缩")
    parser.add_argument("-s", "--with-shebang", action='store_true',
                        help="是否加入`/usr/bin/env python3`作为`Shebang`")
    parser.add_argument("-p", "--with-compile",
                        action='store_true', help="是否仅将编译好的字节码打包,注意python的字节码跨平台兼容但跨大版本不兼容")
    parser.add_argument("-v", "--version", help="查看pyzpacker版本号",
                        action='version', version=f'%(prog)s {__version__}')
    args = parser.parse_args()
    pyzpacker(
        args.source,
        args.main,
        output=args.output,
        with_requirements=args.with_requirements,
        with_compress=args.with_compress,
        with_shebang=args.with_shebang,
        with_compile=args.with_compile)
