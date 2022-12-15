# -*- coding: utf-8 -*-
from apps.api import TransferApi
from apps.log_databus.constants import RETRY_TIMES, INDEX_WRITE_PREFIX
from apps.log_databus.handlers.check_collector.checker.base_checker import Checker
from apps.log_databus.handlers.storage import StorageHandler
from apps.log_esquery.utils.es_client import get_es_client
from apps.log_measure.exceptions import EsConnectFailException


class EsChecker(Checker):
    CHECKER_NAME = "es checker"

    def __init__(self, table_id, bk_data_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table_id = table_id
        self.bk_data_name = bk_data_name
        self.result_table = {}
        self.cluster_config = {}
        self.cluster_id = 0
        # 物理索引列表
        self.indices = []
        self.es_client = None

    def pre_run(self):
        try:
            result = TransferApi.get_result_table_storage(
                {"result_table_list": self.table_id, "storage_type": "elasticsearch"}
            )
            self.result_table = result.get(self.table_id, {})
            self.cluster_config = self.result_table.get("cluster_config", {})
            self.cluster_id = self.cluster_config.get("cluster_id", 0)
        except Exception as e:
            self.append_error_info(f"[TransferApi] [get_result_table_storage] 失败, err: {e}")

    def run(self):
        pass

    def get_indices(self):
        """
        获取物理索引的名称
        """
        indices = None
        # 可能会请求失败, 重试几次
        for i in range(RETRY_TIMES):
            try:
                indices = StorageHandler(self.cluster_id).indices()
                if indices is not None:
                    break
            except Exception as e:  # disable
                self.append_warning_info(f"获取物理索引失败第{i + 1}次, err: {e}")
        if not indices:
            self.append_error_info("获取物理索引为空")
            return
        for i in indices:
            if i["index_pattern"] == self.bk_data_name:
                self.indices = i["indices"]
        if not self.indices:
            self.append_error_info("获取物理索引为空")
            return
        for i in self.indices:
            self.append_normal_info("物理索引: {}, 健康: {}, 状态: {}".format(i["index"], i["health"], i["status"]))

    def get_es_client(self):
        es_client = None
        auth_info = self.result_table.get("auth_info", {})
        username = auth_info.get("username")
        password = auth_info.get("password")
        for i in range(RETRY_TIMES):
            try:
                es_client = get_es_client(
                    version=self.cluster_config["version"],
                    hosts=[self.cluster_config["domain_name"]],
                    username=username,
                    password=password,
                    scheme=self.cluster_config["schema"],
                    port=self.cluster_config["port"],
                    sniffer_timeout=600,
                    verify_certs=False,
                )
                if es_client is not None:
                    break
            except Exception as e:
                self.append_warning_info(f"创建es_client失败第{i + 1}次, err: {e}")

        if es_client and not es_client.ping(params={"request_timeout": 10}):
            self.append_error_info(EsConnectFailException().message)
            return

        self.es_client = es_client

    def get_index_alias(self):
        """获取物理索引的alias情况"""
        if not self.es_client:
            self.append_error_info("es_client不存在, 跳过检查index_alias")
            return
        index_alias_info_dict = self.es_client.indices.get_alias(index=[i["index"] for i in self.indices])
        for i in self.indices:
            # index 物理索引名
            physical_index = i["index"]
            if not index_alias_info_dict.get(physical_index):
                self.append_error_info(f"物理索引: {physical_index} 不存在alias别名")
                continue

            if physical_index.startswith(INDEX_WRITE_PREFIX):
                self.append_warning_info(f"集群存在 write_ 开头的索引: \n{physical_index}")
                return

            self.append_normal_info(f"物理索引: {physical_index} alias别名正常")
