import json

from Deleter import FileSizeComparator, Deleter
from Logger import ThreadSafeLogger

with open("DictProcessResult_result.json", "r", encoding="utf-8") as f:
    data = json.load(f)

logger = ThreadSafeLogger()

file_size_comparator: FileSizeComparator = FileSizeComparator(logger)
deleter = Deleter(data, file_size_comparator, logger)
deleter.delete_by_id()
