from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from FileScanner import IProcesser, BaseProcessResult, FolderScanner

from Deleter import Deleter, FileSizeComparator
from Logger import ThreadSafeLogger


class DictProcessResult(BaseProcessResult):
    def __init__(self, data: defaultdict[str, list[str]]):
        super().__init__(data)

    def _add(self, other: "DictProcessResult") -> "DictProcessResult":
        """重载加法运算符，返回一个新的 DictProcessResult"""
        combined_data: defaultdict[str, list[str]] = self.data.copy()
        for key, value in other.data.items():
            combined_data[key].extend(value)
        return DictProcessResult(combined_data)

    def _iadd(self, other: "DictProcessResult") -> None:
        """重载加法赋值运算符"""
        for key, value in other.data.items():
            self.data[key].extend(value)


class GroupByIdProcesser(IProcesser):
    def process(self, path: Path) -> BaseProcessResult:
        """
        处理数据，返回处理结果。
        这里每个文件的内容是一个以下划线分隔的字符串，第一列是ID，第二列是值。
        返回字典，键为ID，值为对应的值列表。
        """
        name: str = path.name
        split_name: list[str] = name.split("_")
        split_name_index: int = 1
        while (split_name_index < len(split_name)) and (len(split_name[split_name_index]) < 14):
            split_name_index += 1
        result: defaultdict[str, list[str]] = defaultdict(list)
        result[split_name[split_name_index]].append(str(path.resolve()))
        return DictProcessResult(result)

    @property
    def empty_process_result(self) -> BaseProcessResult:
        """返回一个空处理结果"""
        return DictProcessResult(defaultdict(list))


def main(if_test: bool = True):
    logger = ThreadSafeLogger()
    with ThreadPoolExecutor(max_workers=10) as executor:
        scanner = FolderScanner(r"\\server1.sagumesweet.com\aria2", executor, logger, processer=GroupByIdProcesser())
        result = scanner.scan()
        scanner.convert_to_json_file()
        file_size_comparator: FileSizeComparator = FileSizeComparator(logger, executor)
        deleter = Deleter(result.data, file_size_comparator, logger)
        if if_test:
            deleter.delete_by_id()
        else:
            deleter.do_delete().delete_by_id()
    print(len(result.data))


main()
