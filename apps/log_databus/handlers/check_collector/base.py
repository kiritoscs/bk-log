# -*- coding: utf-8 -*-
from typing import Union

from dataclasses import dataclass, asdict, fields
from django.core.cache import cache

from apps.log_databus.constants import (
    CHECK_COLLECTOR_CACHE_KEY_PREFIX,
    CHECK_COLLECTOR_ITEM_CACHE_TIMEOUT,
    CheckStatusEnum,
)


@dataclass
class CheckResult:
    status: str
    infos: list

    to_dict = asdict

    @classmethod
    def from_dict(cls, data: dict):
        init_fields = {f.name for f in fields(cls) if f.init}
        filtered_data = {k: data.pop(k, None) for k in init_fields}
        instance = cls(**filtered_data)
        return instance


class CheckCollectorRecord:
    @staticmethod
    def generate_check_record_id(collector_config_id: int, hosts: str = None) -> str:
        """
        生成检查结果的缓存key
        :param collector_config_id: 采集项ID
        :param hosts: host字符串 example "{bk_cloud_id}:{ip},{bk_cloud_id}:{ip},{bk_cloud_id}:{ip}"
        :return: 检查结果的缓存key
        """
        generate_key_list = [CHECK_COLLECTOR_CACHE_KEY_PREFIX, str(collector_config_id)]
        if hosts:
            generate_key_list.append(hosts)
        return "_".join(generate_key_list)

    @classmethod
    def get_check_result(cls, check_record_id: str) -> Union[CheckResult, None]:
        cache_result = cache.get(check_record_id, None)

        if cache_result:
            return CheckResult.from_dict(cache_result)
        else:
            return None

    def __init__(self, check_record_id: str):
        self.check_record_id = check_record_id
        self.check_record = self.get_check_result(self.check_record_id)

    def is_exist(self) -> bool:
        return self.check_record is not None

    def new_record(self):
        record = CheckResult(status=CheckStatusEnum.WAIT.value, infos=[])
        self.check_record = record
        self.save_check_record()

    def save_check_record(self):
        if not self.is_exist():
            return

        cache.set(self.check_record_id, self.check_record.to_dict(), CHECK_COLLECTOR_ITEM_CACHE_TIMEOUT)

    def get_check_status(self) -> Union[str, None]:
        if not self.is_exist():
            return None
        return self.check_record.status

    def get_infos(self) -> str:
        if not self.is_exist():
            return ""
        return "\n".join(self.check_record.infos)

    def append_info(self, info: str):
        if not self.is_exist():
            return

        self.check_record.infos.append(info)
        self.save_check_record()

    def append_normal_info(self, info: str, prefix: str):
        info = f"[info][{prefix}]{info}"
        self.append_info(info)

    def append_warning_info(self, info: str, prefix: str):
        info = f"[warning][{prefix}]{info}"
        self.append_info(info)

    def append_error_info(self, info: str, prefix: str):
        self.change_status(CheckStatusEnum.FINISH.value)
        info = f"[error][{prefix}]{info}"
        self.append_info(info)

    def change_status(self, status):
        self.check_record.status = status
        self.save_check_record()
