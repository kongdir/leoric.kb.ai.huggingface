import os
import requests
import zipfile
import tempfile
from pathlib import Path
from typing import Optional

# 导入 Rich 库的进度组件
from rich.progress import (
    Progress,
    BarColumn,
    DownloadColumn,
    TransferSpeedColumn,
    TimeRemainingColumn,
    TextColumn
)

def download_and_unzip(
    url: str,
    extract_to: str = "./extracted_files",
    skip_if_not_empty: bool = True
) -> None:
    """
    从指定URL下载ZIP文件并解压到指定目录，使用Rich显示简洁的下载进度
    
    Args:
        url: ZIP文件的下载链接
        extract_to: 解压后的文件保存目录（默认：当前目录下的extracted_files）
        skip_if_not_empty: 若目标文件夹非空则跳过下载解压（默认：True）
    
    Raises:
        requests.exceptions.RequestException: 网络请求相关异常
        zipfile.BadZipFile: ZIP文件损坏或格式错误
        OSError: 文件操作相关异常
    """
    # 1. 检查目标文件夹是否非空，若非空则跳过
    extract_path = Path(extract_to)
    if skip_if_not_empty and extract_path.exists():
        has_files = any(extract_path.iterdir())
        if has_files:
            print(f"⚠️  目标文件夹 {extract_to} 不为空，已跳过下载和解压操作")
            return

    # 创建解压目录（如果不存在）
    extract_path.mkdir(parents=True, exist_ok=True)

    # 初始化总字节数
    total_bytes = 0
    # 先尝试通过HEAD请求获取文件总大小
    try:
        head_response = requests.head(url, timeout=10, allow_redirects=True)
        head_response.raise_for_status()
        total_bytes = int(head_response.headers.get("Content-Length", 0))
    except (requests.exceptions.RequestException, ValueError, KeyError):
        # 若HEAD请求失败，后续从GET响应获取
        total_bytes = 0

    try:
        # 2. 初始化Rich进度条（纯文本简洁样式）
        progress = Progress(
            TextColumn("{task.description}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            DownloadColumn(),
            "•",
            TransferSpeedColumn(),
            "•",
            TimeRemainingColumn(),
        )

        # 3. 开始下载文件（适配大文件，增加超时时间）
        print(f"📥 开始下载文件: {url}")
        # 增加超时时间（大文件下载需要更长连接时间）
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()

        # 补充获取文件总大小（若HEAD请求未获取到）
        if total_bytes == 0:
            total_bytes = int(response.headers.get("Content-Length", 0))

        # 创建临时文件保存ZIP内容
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
            temp_zip_path = temp_zip.name

            # 使用Rich进度条跟踪下载进度
            with progress:
                # 创建下载任务，处理未知大小的情况
                download_task = progress.add_task(
                    description="下载中",
                    total=total_bytes if total_bytes > 0 else None
                )

                # 分块写入文件并更新进度（大文件建议chunk_size=16384）
                for chunk in response.iter_content(chunk_size=16384):
                    if chunk:
                        temp_zip.write(chunk)
                        temp_zip.flush()  # 强制刷新缓冲区
                        progress.update(download_task, advance=len(chunk), refresh=True)

        print("✅ 下载完成")

        # 4. 解压ZIP文件（大文件解压可能耗时，增加提示）
        print(f"📤 开始解压文件到: {extract_to}（大文件解压可能需要几分钟，请耐心等待）")
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            # 打印解压的文件列表（仅显示前10个，避免输出过长）
            extracted_files = zip_ref.namelist()
            print(f"📂 成功解压 {len(extracted_files)} 个文件:")
            for file in extracted_files[:10]:
                print(f"  - {file}")
            if len(extracted_files) > 10:
                print(f"  - ... 还有 {len(extracted_files)-10} 个文件")

    except requests.exceptions.RequestException as e:
        raise Exception(f"下载文件失败: {str(e)}") from e
    except zipfile.BadZipFile as e:
        raise Exception(f"ZIP文件损坏或格式错误: {str(e)}") from e
    except OSError as e:
        raise Exception(f"文件操作失败: {str(e)}") from e
    finally:
        # 清理临时ZIP文件
        if 'temp_zip_path' in locals() and os.path.exists(temp_zip_path):
            try:
                os.unlink(temp_zip_path)
                print("🧹 临时ZIP文件已清理")
            except OSError:
                pass