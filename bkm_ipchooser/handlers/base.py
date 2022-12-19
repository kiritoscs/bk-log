# -*- coding: utf-8 -*-
import typing
import time

from bkm_ipchooser import constants, types
from bkm_ipchooser.api import BkApi
from bkm_ipchooser.query import resource


class BaseHandler:
    @staticmethod
    def get_meta_data(bk_biz_id: int) -> types.MetaData:
        return {"scope_type": constants.ScopeType.BIZ.value, "scope_id": str(bk_biz_id), "bk_biz_id": bk_biz_id}

    @classmethod
    def format_hosts(cls, hosts: typing.List[types.HostInfo], bk_biz_id: int) -> typing.List[types.FormatHostInfo]:
        """
        格式化主机信息
        :param hosts: 尚未进行格式化处理的主机信息
        :return: 格式化后的主机列表
        """
        biz_id__info_map: typing.Dict[int, typing.Dict] = {
            biz_info["bk_biz_id"]: biz_info for biz_info in resource.ResourceQueryHelper.fetch_biz_list()
        }

        # TODO: 暂不支持 >1000
        resp = BkApi.search_cloud_area({"page": {"start": 0, "limit": 1000}})

        if resp.get("info"):
            cloud_id__info_map: typing.Dict[int, typing.Dict] = {
                cloud_info["bk_cloud_id"]: cloud_info["bk_cloud_name"] for cloud_info in resp["info"]
            }
        else:
            # 默认存在直连区域
            cloud_id__info_map = {
                constants.DEFAULT_CLOUD: {
                    "bk_cloud_id": constants.DEFAULT_CLOUD,
                    "bk_cloud_name": constants.DEFAULT_CLOUD_NAME,
                }
            }

        formatted_hosts: typing.List[types.HostInfo] = []
        for host in hosts:
            bk_cloud_id = host["bk_cloud_id"]
            formatted_hosts.append(
                {
                    "meta": BaseHandler.get_meta_data(bk_biz_id),
                    "host_id": host["bk_host_id"],
                    "ip": host["bk_host_innerip"],
                    "ipv6": host.get("bk_host_innerip_v6", ""),
                    "cloud_id": host["bk_cloud_id"],
                    "cloud_vendor": host.get("bk_cloud_vendor", ""),
                    "agent_id": host.get("bk_agent_id", ""),
                    "host_name": host["bk_host_name"],
                    "os_name": host["bk_os_type"],
                    "alive": host.get("status"),
                    "cloud_area": {"id": bk_cloud_id, "name": cloud_id__info_map.get(bk_cloud_id, bk_cloud_id)},
                    "biz": {
                        "id": bk_biz_id,
                        "name": biz_id__info_map.get(bk_biz_id, {}).get("bk_biz_name", bk_biz_id),
                    },
                    # 暂不需要的字段，留作扩展
                    "bk_mem": host["bk_mem"],
                    "bk_disk": host["bk_disk"],
                    "bk_cpu": host["bk_cpu"],
                    # "bk_cpu_architecture": host["bk_cpu_architecture"],
                    # "bk_cpu_module": host["bk_cpu_module"],
                }
            )

        return formatted_hosts

    @classmethod
    def format_host_id_infos(
        cls, hosts: typing.List[types.HostInfo], bk_biz_id: int
    ) -> typing.List[types.FormatHostInfo]:
        """
        格式化主机信息
        :param hosts: 尚未进行格式化处理的主机信息
        :return: 格式化后的主机列表
        """

        formatted_hosts: typing.List[types.HostInfo] = []
        for host in hosts:
            formatted_hosts.append(
                {
                    "meta": BaseHandler.get_meta_data(bk_biz_id),
                    "host_id": host["bk_host_id"],
                    "ip": host["bk_host_innerip"],
                    "ipv6": host.get("bk_host_innerip_v6"),
                    "cloud_id": host["bk_cloud_id"],
                }
            )

        return formatted_hosts

    @classmethod
    def add_latest_label_and_sort(cls, datas: typing.List[typing.Dict]):
        # 添加最近使用标签, 并按照名称排序
        # 用在 动态拓扑, 服务模板, 集群模板
        now_time_unix = time.time()
        # 先根据是否为最近更新分组，再按照名称排序
        latest_groups = []
        other_groups = []
        for data in datas:
            data["is_latest"] = False
            last_time = data["last_time"]
            last_time_unix = time.mktime(time.strptime(last_time, "%Y-%m-%dT%H:%M:%S.%fZ"))
            if last_time_unix >= now_time_unix - constants.TimeEnum.DAY.value:
                data["is_latest"] = True
            other_groups.append(data)
        # 按照名称排序
        latest_groups.sort(key=lambda g: g["name"])
        other_groups.sort(key=lambda g: g["name"])
        datas = latest_groups + other_groups