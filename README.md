# ocr-table-word-demo

## 1. 项目简介

`ocr-table-word-demo` 是一个本地化的表格图片 OCR 转 Word Demo。

它使用开源方案完成主流程：OpenCV 做基础图像预处理，PaddleOCR 做中文 OCR 识别，基于 OCR 文本框坐标做简化表格结构重组，最后使用 `python-docx` 生成可编辑的 `.docx` Word 表格。

本项目不调用任何商业 OCR API，也不调用云端 OCR API。PaddleOCR 首次运行可能会下载开源模型；如果需要完全离线运行，请提前在目标环境缓存 PaddleOCR 模型。

## 2. 当前实现能力

- 支持单张图片输入。
- 支持 PaddleOCR 中文识别。
- 支持基础图像预处理：读取、灰度化、去噪、自适应二值化。
- 支持表格线增强的调试输出，为后续表格线解析预留接口。
- 支持基于 OCR 坐标的简化表格结构重组。
- 支持生成可编辑 `.docx` Word 表格。
- 支持 Docker 构建和运行。
- 支持控制台日志和 `logs/app.log` 文件日志。
- 支持低置信度文本日志提示，并在 Word 中用 `[低置信度]` 标记。
- 尽量保留 OCR 识别出的 `□ / ☑ / ○ / 有 / 无` 等字符；实际效果依赖图片质量和 OCR 模型。

## 3. 当前限制

- 第一版不保证复杂合并单元格完美还原。
- 对严重倾斜、模糊、阴影、透视变形图片效果有限。
- 对无线表格和复杂嵌套表格结构支持有限。
- 手写中文识别准确率依赖 PaddleOCR 模型效果。
- 勾选框识别依赖图片质量和 OCR 效果，当前版本不会强行编造勾选结果。
- 当前版本是 MVP，不是生产级完整系统。

## 4. 项目结构

```text
ocr-table-word-demo/
  input/
    README.md
  output/
    README.md
  logs/
    README.md
  src/
    __init__.py
    main.py
    config.py
    logger.py
    preprocess.py
    ocr_engine.py
    table_parser.py
    word_writer.py
    utils.py
  requirements.txt
  Dockerfile
  .dockerignore
  README.md
  run.sh
```

核心文件说明：

- `src/main.py`：命令行入口，串联预处理、OCR、表格解析、Word 生成。
- `src/config.py`：默认语言、置信度阈值、目录、标题等配置。
- `src/logger.py`：日志初始化，支持控制台和文件日志。
- `src/preprocess.py`：OpenCV 图像预处理，失败时不阻塞 OCR 主流程。
- `src/ocr_engine.py`：PaddleOCR 初始化和输出结构适配。
- `src/table_parser.py`：基于 OCR 坐标聚类成行、推断列、生成二维矩阵。
- `src/word_writer.py`：使用 `python-docx` 生成可编辑 Word 表格。
- `src/utils.py`：目录创建、路径检查、调试图片保存等工具函数。

## 5. 本地运行方式

推荐 Python 3.10 或 Python 3.11。

创建虚拟环境：

```bash
python -m venv .venv
```

Linux / macOS 激活：

```bash
source .venv/bin/activate
```

Windows PowerShell 激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```bash
pip install -r requirements.txt
```

放入输入图片：

```text
input/sample.jpg
```

执行命令：

```bash
python -m src.main --input input/sample.jpg --output output/result.docx
```

开启调试图片输出：

```bash
python -m src.main --input input/sample.jpg --output output/result.docx --debug
```

也可以使用脚本：

```bash
bash run.sh input/sample.jpg output/result.docx
```

## 6. Docker 运行方式

构建镜像：

```bash
docker build -t ocr-table-word-demo .
```

Linux / macOS 运行：

```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output -v $(pwd)/logs:/app/logs ocr-table-word-demo python -m src.main --input input/sample.jpg --output output/result.docx
```

Windows PowerShell 运行：

```powershell
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output -v ${PWD}/logs:/app/logs ocr-table-word-demo python -m src.main --input input/sample.jpg --output output/result.docx
```

说明：PaddleOCR / paddlepaddle 依赖较大，首次 `pip install` 或 Docker 构建可能较慢。首次 OCR 运行也可能下载开源模型。

## 7. 输入输出说明

- 输入图片放在 `input/` 目录，例如 `input/sample.jpg`。
- 输出 Word 默认生成到 `output/result.docx`。
- 日志默认输出到控制台和 `logs/app.log`。
- 开启 `--debug` 后，灰度图、去噪图、二值化图、表格线增强图会保存到 `logs/debug/`。

## 8. 运行视频录制建议

演示时建议按这个顺序录制：

1. 展示 `input/sample.jpg` 原始表格图片。
2. 执行命令行 OCR 转换命令。
3. 展示控制台 OCR 数量、低置信度提示、输出路径日志。
4. 打开 `output/result.docx`。
5. 在 Word 中点击单元格，展示生成结果是可编辑表格。

## 9. 后续优化方向

- 引入更强的表格结构识别模型。
- 增加合并单元格识别。
- 增加透视矫正和更稳定的倾斜矫正。
- 增加低置信度人工复核界面或复核导出。
- 针对业务表格样本微调 OCR 或结构识别模型。
- 支持批量文件夹处理。
- 支持 FastAPI 服务化封装。
- 支持更稳定的勾选框识别。

## 10. 验收标准

- 命令能正常执行。
- 控制台能看到处理开始、OCR 数量、低置信度文本、输出路径等日志。
- `output/result.docx` 能生成。
- Word 文件能打开，并且表格内容可编辑。
- Docker 镜像能构建，并能通过挂载目录完成转换。

## 11. 常见问题

### 1. 为什么首次运行很慢？

PaddleOCR / paddlepaddle 依赖较大，首次安装会比较慢。首次 OCR 运行还可能下载开源模型文件，建议录屏前先提前运行一次，缓存依赖和模型。

### 2. Python 3.13 可以直接安装吗？

不建议。`paddlepaddle` 对 Python 版本和平台有要求，本项目推荐 Python 3.10 或 Python 3.11。Dockerfile 默认使用 `python:3.10-slim`，更适合交付演示。

### 3. OCR 失败时会不会没有输出？

当前版本会尽量生成 Word 文件。如果 OCR 初始化或识别失败，程序会写日志，并生成包含“未识别到有效表格内容”的 `.docx`，方便交付流程不中断。

### 4. 表格还原为什么不完全一致？

第一版使用 OCR 文本框坐标聚类来重组二维表格，不包含复杂合并单元格、透视矫正和专业表格结构模型，所以复杂表格只能作为近似结果。

### 5. Docker 构建失败怎么办？

优先检查网络、Docker Desktop 是否正常运行、镜像源是否可访问。PaddleOCR 相关依赖安装时间较长，构建阶段需要耐心等待。

## 12. 示例命令汇总

本地运行：

```bash
python -m src.main --input input/sample.jpg --output output/result.docx
```

本地运行并输出调试图片：

```bash
python -m src.main --input input/sample.jpg --output output/result.docx --conf-threshold 0.70 --debug
```

Docker 构建：

```bash
docker build -t ocr-table-word-demo .
```

Docker 运行：

```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output -v $(pwd)/logs:/app/logs ocr-table-word-demo python -m src.main --input input/sample.jpg --output output/result.docx
```

## Final Docker Demo

Build image:

docker build -t ocr-table-word-demo .

Run demo:

docker run --rm -v "${PWD}\input:/app/input" -v "${PWD}\output:/app/output" -v "${PWD}\logs:/app/logs" -v "${PWD}\models:/root/.EasyOCR" ocr-table-word-demo python -m src.main --input input/sample_enhanced.png --output output/result.docx --debug

Project features:

- Input table image
- Image preprocessing
- OCR recognition
- Table structure reconstruction
- Editable Word table generation
- Docker-based local deployment
- Log and debug image output

Note:

The current delivery version uses EasyOCR as a Docker-compatible OCR fallback. The original design can be switched to PaddleOCR in a stable Paddle runtime environment. For noisy or low-resolution scanned images, OCR results should be reviewed together with the original image.
