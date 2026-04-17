import os
import datetime
from typing import Dict, Any, List

try:
    from kubernetes import client, config
except ImportError:
    raise ImportError("请安装 kubernetes 包: pip install kubernetes")

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    raise ImportError("请安装 jinja2 包: pip install jinja2")


class K8sReportSkill:
    """
    K8s 集群巡检 Skill
    用于 AI Agent 框架的 Kubernetes 集群状态巡检功能。
    包含节点、Pod、Deployment 状态检查，以及近期警告事件提取，最终生成可用于邮件通知的 HTML。
    """

    def __init__(self, kubeconfig_path: str = None):
        """
        初始化 Kubernetes 客户端
        :param kubeconfig_path: 可选的 kubeconfig 文件路径，默认自动寻找或使用集群内配置
        """
        self._init_k8s_client(kubeconfig_path)

    def _init_k8s_client(self, kubeconfig_path: str = None):
        try:
            # 1. 如果显式传递了 kubeconfig 或者是默认在某些环境变量里，尝试加载
            if kubeconfig_path and os.path.exists(kubeconfig_path):
                config.load_kube_config(config_file=kubeconfig_path)
            else:
                # 2. 检查默认的 ~/.kube/config 路径
                default_kubeconfig = os.path.expanduser("~/.kube/config")
                if os.path.exists(default_kubeconfig):
                    config.load_kube_config(config_file=default_kubeconfig)
                else:
                    # 3. 如果 ~/.kube/config 不存在，尝试 In-Cluster 模式
                    config.load_incluster_config()
        except Exception as e:
            raise RuntimeError(f"无法加载 Kubernetes 配置 (KubeConfig 或 InCluster 均失败): {e}")

        # Api 客户端实例
        self.v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.custom_api = client.CustomObjectsApi()
        self.version_api = client.VersionApi()

    def _parse_cpu(self, cpu_str: str) -> float:
        if not cpu_str or cpu_str == 'N/A': return 0.0
        cpu_str = str(cpu_str)
        if cpu_str.endswith('m'):
            return float(cpu_str[:-1]) / 1000.0
        elif cpu_str.endswith('n'):
            return float(cpu_str[:-1]) / 1000000000.0
        try:
            return float(cpu_str)
        except:
            return 0.0

    def _parse_mem(self, mem_str: str) -> float:
        if not mem_str or mem_str == 'N/A': return 0.0
        mem_str = str(mem_str)
        units = {"Ki": 1/1024/1024, "Mi": 1/1024, "Gi": 1, "Ti": 1024, "Pi": 1024*1024, "K": 1000/(1024**3), "M": 1000**2/(1024**3), "G": 1000**3/(1024**3)}
        for unit, factor in units.items():
            if mem_str.endswith(unit):
                try:
                    return float(mem_str[:-len(unit)]) * factor
                except:
                    return 0.0
        try:
            return float(mem_str) / (1024**3)
        except:
            return 0.0

    def get_cluster_info(self) -> Dict[str, str]:
        """查询当前集群的基础/版本状态"""
        version = self.version_api.get_code()
        return {
            "git_version": version.git_version,
            "platform": version.platform,
            "go_version": version.go_version
        }

    def get_namespaces(self) -> List[str]:
        """获取当前集群的所有命名空间名称"""
        ns_list = self.v1.list_namespace().items
        return [ns.metadata.name for ns in ns_list]

    def get_nodes_status(self) -> Dict[str, Any]:
        """查询当前集群的节点状态，包括健康、角色及资源使用率"""
        nodes = self.v1.list_node().items
        node_stats = []
        cluster_totals = {
            "cpu_usage": 0.0, "cpu_alloc": 0.0,
            "mem_usage": 0.0, "mem_alloc": 0.0,
            "pods_usage": 0, "pods_alloc": 0
        }

        # 尝试获取 resources metrics（需要 metrics-server 支持）
        metrics = {}
        try:
            node_metrics = self.custom_api.list_cluster_custom_object(
                group="metrics.k8s.io",
                version="v1beta1",
                plural="nodes"
            )
            for item in node_metrics.get('items', []):
                metrics[item['metadata']['name']] = item['usage']
        except Exception:
            pass  # 如果集群没有安装 metrics-server 则跳过

        # 计算落在每个节点上的 Pod 数量
        pods = self.v1.list_pod_for_all_namespaces().items
        node_pods_count = {}
        for pod in pods:
            node_name = pod.spec.node_name
            if node_name:
                node_pods_count[node_name] = node_pods_count.get(node_name, 0) + 1

        for node in nodes:
            name = node.metadata.name
            
            # 判断 Ready 状态
            ready_condition = next((c for c in node.status.conditions if c.type == "Ready"), None)
            status_text = "Ready" if (ready_condition and ready_condition.status == "True") else "NotReady"
            
            # 提取资源使用率和分配容量
            usage = metrics.get(name, {})
            allocatable = node.status.allocatable or {}
            
            cpu_usage = usage.get('cpu', 'N/A')
            cpu_alloc = allocatable.get('cpu', 'N/A')
            
            mem_usage = usage.get('memory', 'N/A')
            mem_alloc = allocatable.get('memory', 'N/A')
            
            pods_usage = str(node_pods_count.get(name, 0))
            pods_alloc = allocatable.get('pods', 'N/A')

            # 累加到统计
            cluster_totals["cpu_usage"] += self._parse_cpu(cpu_usage)
            cluster_totals["cpu_alloc"] += self._parse_cpu(cpu_alloc)
            cluster_totals["mem_usage"] += self._parse_mem(mem_usage)
            cluster_totals["mem_alloc"] += self._parse_mem(mem_alloc)
            cluster_totals["pods_usage"] += int(pods_usage)
            try:
                cluster_totals["pods_alloc"] += int(pods_alloc)
            except:
                pass

            # 提取角色
            roles = [k.split('/')[-1] for k in (node.metadata.labels or {}).keys() if 'node-role.kubernetes.io' in k]
            if not roles:
                roles = ['worker']

            node_stats.append({
                "name": name,
                "status": status_text,
                "roles": roles,
                "cpu_usage": f"{cpu_usage} / {cpu_alloc}",
                "memory_usage": f"{mem_usage} / {mem_alloc}",
                "pods_usage": f"{pods_usage} / {pods_alloc}",
                "kubelet_version": node.status.node_info.kubelet_version
            })

        return {
            "list": node_stats,
            "totals": cluster_totals
        }

    def get_pods_status(self) -> Dict[str, Any]:
        """查询当前集群的 Pod 状态，按照正常和不正常分类"""
        pods = self.v1.list_pod_for_all_namespaces().items
        normal_pods = []
        abnormal_pods = []

        for pod in pods:
            phase = pod.status.phase
            is_abnormal = False
            reason_text = phase

            if phase not in ["Running", "Succeeded"]:
                is_abnormal = True

            # 深度检查容器运行状态 (例如 CrashLoopBackOff, ImagePullBackOff 等)
            restarts = 0
            if pod.status.container_statuses:
                for cs in pod.status.container_statuses:
                    restarts += cs.restart_count
                    if cs.state.waiting and cs.state.waiting.reason:
                        is_abnormal = True
                        reason_text = f"{phase} ({cs.state.waiting.reason})"
                    elif cs.state.terminated and cs.state.terminated.exit_code != 0:
                        is_abnormal = True
                        reason_text = f"Terminated ({cs.state.terminated.reason or cs.state.terminated.exit_code})"
                    
                    # 也可以定义重启次数过多为异常
                    if cs.restart_count >= 10:
                        is_abnormal = True
                        reason_text = f"HighRestarts ({cs.restart_count})"

            pod_info = {
                "namespace": pod.metadata.namespace,
                "name": pod.metadata.name,
                "status": phase,
                "reason": reason_text,
                "restarts": restarts
            }

            if is_abnormal:
                abnormal_pods.append(pod_info)
            else:
                normal_pods.append(pod_info)

        return {"normal": normal_pods, "abnormal": abnormal_pods, "total": len(pods)}

    def get_deployments_status(self) -> Dict[str, Any]:
        """查询 Deployments 状态，识别由于配额或调度导致副本不齐的异常情况 (补充的重要属性)"""
        deployments = self.apps_v1.list_deployment_for_all_namespaces().items
        abnormal_deps = []
        
        for dep in deployments:
            desired = dep.spec.replicas or 0
            available = dep.status.available_replicas or 0
            
            # 如果期望副本大于可用副本数，视为异常
            if desired > 0 and available < desired:
                abnormal_deps.append({
                    "namespace": dep.metadata.namespace,
                    "name": dep.metadata.name,
                    "desired": desired,
                    "available": available
                })
                
        return {"abnormal": abnormal_deps, "total": len(deployments)}

    def get_recent_warnings(self) -> List[Dict[str, Any]]:
        """查询最近 1 小时内集群内的警告事件 (补充的重要属性)"""
        events = self.v1.list_event_for_all_namespaces().items
        warnings = []
        now = datetime.datetime.now(datetime.timezone.utc)
        
        for event in events:
            if event.type == "Warning":
                event_time = event.last_timestamp or event.event_time
                if event_time and (now - event_time).total_seconds() < 3600:
                    warnings.append({
                        "namespace": event.involved_object.namespace,
                        "kind": event.involved_object.kind,
                        "name": event.involved_object.name,
                        "reason": event.reason,
                        "message": event.message,
                        "time": event_time.strftime("%Y-%m-%d %H:%M:%S UTC")
                    })
                    
        return warnings

    def get_pv_pvc_status(self) -> Dict[str, Any]:
        """查询当前集群中 PV 和 PVC 的状态，筛选出异常的资源"""
        try:
            pvs = self.v1.list_persistent_volume().items
            pvcs = self.v1.list_persistent_volume_claim_for_all_namespaces().items
        except Exception:
            # 某些权限不足的情况下可能无法读取全量PV
            pvs = []
            pvcs = []
            
        abnormal_pvs = []
        for pv in pvs:
            # PV 常规状态: Available, Bound, Released, Failed
            phase = pv.status.phase
            if phase in ["Failed", "Released"]:
                capacity = pv.spec.capacity.get('storage', 'N/A') if pv.spec.capacity else 'N/A'
                claim = f"{pv.spec.claim_ref.namespace}/{pv.spec.claim_ref.name}" if pv.spec.claim_ref else "None"
                abnormal_pvs.append({
                    "name": pv.metadata.name,
                    "status": phase,
                    "capacity": capacity,
                    "claim": claim
                })
                
        abnormal_pvcs = []
        for pvc in pvcs:
            # PVC 常规状态: Pending, Bound, Lost
            phase = pvc.status.phase
            if phase in ["Pending", "Lost"]:
                request_storage = pvc.spec.resources.requests.get('storage', 'N/A') if pvc.spec.resources and pvc.spec.resources.requests else 'N/A'
                abnormal_pvcs.append({
                    "namespace": pvc.metadata.namespace,
                    "name": pvc.metadata.name,
                    "status": phase,
                    "volume": pvc.spec.volume_name or "None",
                    "request": request_storage
                })

        return {
            "pvs": {"abnormal": abnormal_pvs, "total": len(pvs)},
            "pvcs": {"abnormal": abnormal_pvcs, "total": len(pvcs)}
        }

    def generate_html_report(self) -> str:
        """
        整合所有巡检数据，渲染并返回 HTML 源码。
        """
        # 1. 抓取各类数据
        report_data = {
            "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cluster_info": self.get_cluster_info(),
            "namespaces": self.get_namespaces(),
            "nodes": self.get_nodes_status(),
            "pods": self.get_pods_status(),
            "deployments": self.get_deployments_status(),
            "storage": self.get_pv_pvc_status(),
            "warnings": self.get_recent_warnings()
        }

        # 2. 设置并渲染 Jinja2 模板
        templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
        env = Environment(loader=FileSystemLoader(templates_dir))
        
        # 错误捕获，确保即使找不到模板也能抛出明确异常
        try:
            template = env.get_template('report.html')
        except Exception as e:
            raise FileNotFoundError(f"找不到报告模板: {os.path.join(templates_dir, 'report.html')} -> {e}")
            
        return template.render(data=report_data)


# ------------------------------------------------------------
# 接口封装（可根据实际的 Agent 引擎进行装饰微调）
# ------------------------------------------------------------
def run_k8s_inspection_skill(kubeconfig_path: str = None) -> str:
    """
    Skill: K8s巡检
    运行该函数即进行对底层k8s集群的完整巡检检查，并构建 HTML 报告用于发送邮件等。
    返回的内容为生成的纯 HTML 代码。
    """
    skill = K8sReportSkill(kubeconfig_path=kubeconfig_path)
    html_content = skill.generate_html_report()
    return html_content

if __name__ == "__main__":
    # 本地直接测试生成
    print("开始测试 Kubernetes 集群巡检...")
    try:
        report_html_string = run_k8s_inspection_skill()
        print(report_html_string)
    except Exception as e:
        print(f"巡检失败: {e}")
