import os
import stat
import zipapp
import shutil
import compileall
import platform
import subprocess
import chardet
from pathlib import Path
from typing import Optional, Callable, Any, Iterable


def delete_source(root_path: Path, *,
                  file_predication: Optional[Callable[[Path], bool]] = None,
                  dir_predication: Optional[Callable[[Path], bool]] = None,
                  dir_iter_filter: Optional[Callable[[Path], bool]] = None) -> None:
    """删除源文件.
    file_predication和dir_predication必须至少有一个.
    Args:
        root_path (Path): [description]
        file_predication (Optional[Callable]): 用于判断文件是否要被删除的谓词,参数为p:path
        dir_predication (Optional[Callable]): 用于判断文件夹是否要被删除的谓词,参数为p:path
        dir_iter_filter (Optional[Callable]): 用于过滤目录中不用迭代的部分
    """
    if not callable(file_predication):
        file_predication = None
    if not callable(dir_predication):
        dir_predication = None
    if not callable(dir_iter_filter):
        dir_iter_filter = None

    def remove_readonly(func: Callable[[str], Any], path: str, _: Any) -> object:
        """Clear the readonly bit and reattempt the removal."""
        os.chmod(path, stat.S_IWRITE)
        return func(path)

    def _delete_source(p: Path) -> None:
        """递归的删除根目录下需要删除的文件.
        Args:
            p (Path): 要判断时候要删除的路径
        """
        if p.is_file():
            if file_predication and file_predication(p):
                os.remove(p)
        elif p.is_dir():
            if dir_predication and dir_predication(p):
                # 文件夹-删除
                try:
                    shutil.rmtree(p, onerror=remove_readonly)
                except Exception as e:
                    print(f"rmtree {p} get error {str(e)}")
            else:
                # 文件夹-继续遍历
                iterdir: Iterable[Path] = p.iterdir()
                if dir_iter_filter:
                    iterdir = filter(dir_iter_filter, p.iterdir())
                for child_path in iterdir:
                    _delete_source(child_path)
    if any([callable(file_predication), callable(dir_predication)]):
        _delete_source(root_path)
    else:
        raise AttributeError("file_predication和dir_predication必须至少有一个.")


def _delete_py_source(root_path: Path) -> None:
    """将python源码的.py文件删除.
    这是一个递归操作的函数.
    Args:
        p (Path): 要删除py文件的文件夹
    """
    delete_source(
        root_path,
        file_predication=lambda p: p.suffix == ".py",
        dir_predication=lambda p: p.name == "__pycache__"
    )


def pyzpacker(source: str, main: str, *, output: Optional[str] = None, with_requirements: Optional[str] = None,
              with_compress: bool = False, with_shebang: bool = False, with_compile: bool = False) -> None:
    cwd = Path.cwd()
    source_path = Path(source)
    module_name = source_path.name
    pyz_name = module_name
    temp_path = cwd.joinpath("temp_app")
    temp_module_path = temp_path.joinpath(module_name)
    if output:
        output_dir = Path(output)
        if output_dir.exists():
            if not output_dir.is_dir():
                raise AttributeError("output must be a dir")
        else:
            output_dir.mkdir(parents=True)
    else:
        output_dir = cwd
    if with_shebang:
        interpreter = "/usr/bin/env python3"
    else:
        interpreter = None

    try:
        shutil.copytree(
            source_path,
            temp_module_path
        )
        if with_compile:
            compileall.compile_dir(
                temp_module_path, force=True, legacy=True, optimize=2)
            _delete_py_source(temp_module_path)
            python_version_tuple = platform.python_version_tuple()
            major = python_version_tuple[0]
            minor = python_version_tuple[1]
            pyz_name = f"{module_name}-py{major}.{minor}"
        if with_requirements:
            command = f'python -m pip install -r {with_requirements} --target temp_app'
            default_environ = dict(os.environ)
            try:
                res = subprocess.run(
                    command,
                    capture_output=True,
                    shell=True,
                    check=True,
                    cwd=cwd,
                    env=default_environ
                )
            except subprocess.CalledProcessError as ce:
                print(f"""命令: {command} 执行失败""")
                if ce.stderr:
                    encoding = chardet.detect(ce.stderr).get("encoding")
                    if encoding:
                        content = ce.stderr.decode(encoding).strip()
                        print(content)
                else:
                    encoding = chardet.detect(ce.stdout).get("encoding")
                    if encoding:
                        content = ce.stdout.decode(encoding).strip()
                        print(content)
                raise ce
            except Exception as e:
                print(f"""命令: {command} 执行失败""")
                raise e
            else:
                content = ""
                if res.stdout:
                    encoding = chardet.detect(res.stdout).get("encoding")
                    if encoding:
                        content = res.stdout.decode(encoding).strip()
                        print(content)
        target = output_dir.joinpath(f"{pyz_name}.pyz")
        zipapp.create_archive(
            temp_path,
            target=target,
            interpreter=interpreter,
            main=main,
            compressed=with_compress
        )
    finally:
        if temp_path.exists():
            shutil.rmtree(temp_path)
