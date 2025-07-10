from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Optional

from Logger import ThreadSafeLogger, Logger


class FileSizeComparator:
    def __init__(self, logger: ThreadSafeLogger, max_workers: int = 10):
        self._file_list: list[str] = []
        self._max_workers = max_workers
        self._size_map: dict[int, list[tuple[str, float]]] = defaultdict(list)
        self._logger = logger

    @property
    def file_list(self) -> list[str]:
        """获取文件列表"""
        return self._file_list

    @file_list.setter
    def file_list(self, files: list[str]) -> None:
        """设置文件列表"""
        if not self._file_list:
            self._file_list.extend(files)
        else:
            self._file_list = files

    def _get_size(self, file: str) -> Optional[tuple[int, float, str]]:
        path = Path(file)
        self._logger.debug("获取文件大小: %s", str(path))
        if path.is_file():
            stat = path.stat()
            return stat.st_size, stat.st_mtime, file
        return None

    def compare(self) -> dict[str, list[str]]:
        """比较文件大小，返回大小相同的文件集合（文件大小作为字符串键）"""
        self._logger.info("开始比较文件大小")
        with ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            for result in executor.map(self._get_size, self._file_list):
                if result is None:
                    continue
                size, time, file = result
                self._size_map[size].append((file, time))
                self._size_map[size].sort(key=lambda x: x[1], reverse=True)
        return {str(size): [file[0] for file in files] for size, files in self._size_map.items() if len(files) > 1}


class Deleter:
    def __init__(self, data: dict[str, list[str]], fileSizeComparator: FileSizeComparator, logger: Logger, retry_count: int = 5):
        self._data: dict[str, list[str]] = data
        self._if_exists: bool = False
        self._retry_count: int = retry_count
        self._fileSizeComparator: FileSizeComparator = fileSizeComparator
        self._logger: Logger = logger

    def if_exists(self) -> "Deleter":
        """是否在删除前检查文件是否存在"""
        self._if_exists = True
        return self

    def _find_same_by_id(self) -> dict[str, list[str]]:
        """
        查找具有相同ID的条目。
        假设ID是数据字典的键，值是一个列表，包含所有具有该ID的条目的路径。
        """
        result: dict[str, list[str]] = {k: v for k, v in self._data.items() if len(v) > 1}
        return result

    def _try_to_delete(self, path: Path, count: int = 1) -> None:
        """
        尝试删除具有相同ID的条目。
        如果没有找到相同ID的条目，则不执行任何操作。
        """
        try:
            if self._if_exists:
                if path.exists() and path.is_file():
                    self._logger.info("Deleting file: %s", str(path))
                    path.unlink()
            else:
                self._logger.info("testing to delete %s", str(path))
                return None

        except FileNotFoundError:
            self._logger.error(f"File {path} not found, skipping deletion.")
            return None
        except PermissionError:
            if count < self._retry_count:
                self._logger.warning(f"Permission denied for {path}, retrying ({count}/{self._retry_count})...")
                self._try_to_delete(path, count + 1)
            else:
                self._logger.error(f"Failed to delete {path} after {self._retry_count} attempts.")
                return None
        return None

    def _delete_by_size(self, paths: list[str | Path]) -> None:
        """
        根据文件大小删除具有相同大小的条目，保留最新的一个。
        字典包含大小和路径。
        """
        if isinstance(paths[0], Path):
            paths = [str(p) for p in paths]
        self._fileSizeComparator.file_list = paths
        same_size_entries = self._fileSizeComparator.compare()
        for size, files in same_size_entries.items():
            # 保留最新的一个
            self._logger.info(f"保留大小为 {size} 的最新文件: {files[0]}")
            self._logger.info("Deleting file: %s", files[1:])
            to_delete = files[1:]
            for path in to_delete:
                if self._if_exists:
                    self._try_to_delete(path=Path(path))
        self._if_exists = False

    def _delete_by_date(self, paths: list[str]) -> None:
        """
        根据文件修改时间删除具有相同修改时间的条目，保留最新的一个。
        字典包含修改时间和路径。
        """
        self._logger.debug("通过上传时间删除视频")
        same_date_entries: dict[str, list[Path]] = defaultdict(list)
        for path in paths:
            p: Path = Path(path)
            date: str = p.parent.name
            same_date_entries[date].append(p)
        latest_date_str = max(same_date_entries.keys(), key=lambda d: datetime.strptime(d, '%Y-%m-%d'))
        self._logger.debug(f"最新的日期是: {latest_date_str}，包括 {same_date_entries[latest_date_str]}")
        if len(same_date_entries.items()) != 1:
            for date_str, ps in same_date_entries.items():
                if date_str != latest_date_str:
                    for p in ps:
                        self._logger.info(f"删除日期为 {date_str} 的文件: {p}")
                        self._try_to_delete(path=p)
        else:
            self._logger.debug(f"没有其他日期，保留最新的日期 {latest_date_str} 的文件")
        if len(same_date_entries[latest_date_str]) > 1:
            self._logger.info(f"最新日期 {latest_date_str} 的文件包含多个值： {same_date_entries[latest_date_str]}")
            self._delete_by_size(same_date_entries[latest_date_str])

    def delete_by_id(self):
        """
        删除具有相同ID的条目，保留最新的一个。
        字典包含ID和路径。
        """
        same_id_entries = self._find_same_by_id()
        for video_id, paths in same_id_entries.items():
            # 保留最新的一个
            self._logger.debug(f"处理 ID {video_id} 的条目，判断文件日期")
            self._delete_by_date(paths)

        self._if_exists = False
