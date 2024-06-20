# $ pyzpacker

+ version: 0.0.1
+ status: dev
+ author: hsz
+ email: hsz1273327@gmail.com

## Description

将纯python项目模块打包为pyz包.

+ keywords: pyz, zip

## Features

+ 将纯python模块打包为pyz包
+ 可选的进行精简大小
+ 可选的包含依赖
+ 仅支持python 3.10+

## Install

```bash
python -m pip install pyzpacker
```

## Usage

```bash
pyzpacker [options] <你的项目目录>

```

默认查找项目目录下cmd目录下的`main`函数作为入口