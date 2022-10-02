"""
Tencent is pleased to support the open source community by making BK-LOG 蓝鲸日志平台 available.
Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
BK-LOG 蓝鲸日志平台 is licensed under the MIT License.
License for BK-LOG 蓝鲸日志平台:
--------------------------------------------------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from apps.utils.log import logger
from apps.api import BcsCcApi, BcsApi
from apps.log_search.models import Space
from apps.utils.thread import MultiExecuteFunc
from bkm_space.define import SpaceTypeEnum


class BcsHandler:
    @classmethod
    def list_bcs_shared_cluster_namespace(cls, cluster_id):
        namespaces = BcsCcApi.list_shared_clusters_ns(cluster_id=cluster_id)
        # TODO do some translate
        return namespaces

    @classmethod
    def list_bcs_cluster(cls, bk_biz_id=None) -> list:
        if bk_biz_id is None:
            logger.warning("[forbidden]query bcs cluster, but not bk_biz_id")
            return []

        space = Space.objects.get(bk_biz_id=bk_biz_id)
        if space.space_type_id == SpaceTypeEnum.BKCC.value:
            bcs_projects = BcsCcApi.list_project()
            # bcs_project_name_map = {p["project_id"]: p["project_name"] for p in bcs_projects}
            bcs_projects = [p for p in bcs_projects if str(p["cc_app_id"]) == str(bk_biz_id)]
            multi_execute_func = MultiExecuteFunc()
            for project in bcs_projects:
                multi_execute_func.append(
                    project["project_id"],
                    BcsApi.list_cluster_by_project_id,
                    {"projectID": project["project_id"], "no_request": True},
                    use_request=False,
                )
            bcs_result = multi_execute_func.run()
        elif space.space_type_id == SpaceTypeEnum.BCS.value:
            clusters = BcsApi.list_cluster_by_project_id({"projectID": space.space_id})
            bcs_result = {space.space_id: clusters}
        else:
            bcs_result = {}

        result = []
        for project_id, clusters in bcs_result.items():
            if not clusters:
                continue
            for cluster in clusters:
                result.append(
                    {
                        # "area_name": bcs_area_name_map.get(cluster["area_id"], cluster["area_id"]),
                        # "project_name": bcs_project_name_map.get(project_id, project_id),
                        "project_id": project_id,
                        "cluster_id": cluster["clusterID"],
                        "cluster_name": cluster["clusterName"],
                        "region": cluster["region"],
                        # "disable": cluster["disable"],
                        "environment": cluster["environment"],
                        "status": cluster["status"],
                        "engine_type": cluster["engineType"],
                        "is_shared": cluster["is_shared"],
                    }
                )
        return result
