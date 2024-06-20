import os
import stat
import zipapp
import shutil
import compileall
import subprocess
from pathlib import Path
from typing import Optional, Callable, Any


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
        dir_iter_filter (Optional[Callable]): 用于过夏季目录中不用迭代的部分
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
        else:
            if dir_predication and dir_predication(p):
                try:
                    shutil.rmtree(p, onerror=remove_readonly)
                except Exception as e:
                    print(e)
            for child_path in filter(dir_iter_filter, p.iterdir()):
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
        file_predication=lambda p: p.suffix == ".py" and p.name not in (
            "__main__.py", "__init__.py"),
        dir_predication=lambda p: p.name == "__pycache__"
    )


def pyzpacker(source: str, main: str, *, output: Optional[str] = None, with_requirements: Optional[str] = None,
              with_compress: bool = False, with_interpreter: bool = False, with_compile: bool = False) -> None:

    cwd = Path.cwd()
    if output:
        output_dir = Path("output")
    else:
        output_dir = cwd

    if with_interpreter:
        interpreter = "/usr/bin/env python3"
    else:
        interpreter = None
    temp_path = cwd.joinpath("temp_app")
    try:
        source_path = Path(source)
        module_name = source_path.name
        temp_module_path = temp_path.joinpath(module_name)
        shutil.copytree(
            source_path,
            temp_module_path
        )
        if with_compile:
            for p in temp_module_path.iterdir():
                compileall.compile_dir(p, force=True, legacy=True, optimize=2)
                if p.is_dir():
                    _delete_py_source(p)

        if with_requirements:
            command = 'python -m pip install -r {with_requirements} --target temp_app'
            default_environ = dict(os.environ)
            subprocess.run(command, capture_output=True, shell=True,
                           check=True, cwd=cwd, env=default_environ)

        zipapp.create_archive(
            temp_path,
            target=output_dir.joinpath(f"{module_name}.pyz"),
            interpreter=interpreter,
            main=main,
            compressed=with_compress
        )
    finally:
        if temp_path.exists():
            shutil.rmtree(temp_path)
