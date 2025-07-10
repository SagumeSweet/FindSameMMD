from pathlib import Path

from Deleter import Deleter, FileSizeComparator
from FolderScanner import FolderScanner
from Logger import ThreadSafeLogger
from Processer import IProcesser, BaseProcessResult


class DictProcessResult(BaseProcessResult):
    def __init__(self, data: dict[str, list[str]]):
        super().__init__(data)

    def _add(self, other: "DictProcessResult") -> "DictProcessResult":
        """重载加法运算符，返回一个新的 DictProcessResult"""
        combined_data: dict[str, list[str]] = self.data.copy()
        for key, value in other.data.items():
            if key in combined_data:
                combined_data[key].extend(value)
            else:
                combined_data[key] = value
        return DictProcessResult(combined_data)

    def _iadd(self, other: "DictProcessResult") -> None:
        """重载加法赋值运算符"""
        for key, value in other.data.items():
            if key in self.data:
                self.data[key].extend(value)
            else:
                self.data[key] = value


class GroupByIdProcesser(IProcesser):
    def process(self, path: Path) -> BaseProcessResult:
        """
        处理数据，返回处理结果。
        这里假设每个文件的内容是一个以逗号分隔的字符串，第一列是ID，第二列是值。
        返回字典，键为ID，值为对应的值列表。
        """
        name: str = path.name
        split_name: list[str] = name.split("_")
        split_name_index: int = 1
        while (split_name_index < len(split_name)) and (len(split_name[split_name_index]) < 14):
            split_name_index += 1
        result: dict[str, list[str]] = {split_name[split_name_index]: [str(path.resolve())]}
        return DictProcessResult(result)

    @property
    def empty_process_result(self) -> BaseProcessResult:
        """返回一个空处理结果"""
        return DictProcessResult({})


class SuffixProcesser(IProcesser):
    def process(self, path: Path) -> BaseProcessResult:
        """
        处理数据，返回处理结果。
        返回字典，键为文件后缀名，值为对应的文件列表。
        """
        suffix = path.suffix.lower()
        return DictProcessResult({suffix: [str(path.resolve())]})

    @property
    def empty_process_result(self) -> BaseProcessResult:
        """返回一个空处理结果"""
        return DictProcessResult({})


def main():
    logger = ThreadSafeLogger()
    with FolderScanner(r"\\server1.sagumesweet.com\aria2", logger, processer=GroupByIdProcesser()) as scanner:
        # 扫描文件夹并获取结果
        result = scanner.scan()
        # 将结果转换为 JSON 文件
        scanner.convert_to_json_file()
    file_size_comparator: FileSizeComparator = FileSizeComparator(logger)
    deleter = Deleter(result.data, file_size_comparator, logger)
    deleter.if_exists().delete_by_id()
    print(len(result.data))


main()
