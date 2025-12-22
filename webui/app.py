#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenVPN Web 管理界面
提供简单易用的图形化配置和管理功能
"""

import os
import subprocess
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from functools import wraps

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# 创建日志过滤器，过滤掉 404 和不重要的访问日志
class IgnoreHealthCheckFilter(logging.Filter):
    def filter(self, record):
        # 忽略 404 日志
        if "404" in record.getMessage():
            return False
        # 忽略 /demo/* 路径的所有日志
        if "/demo/" in record.getMessage():
            return False
        # 忽略健康检查路径
        if "/health" in record.getMessage() or "/ping" in record.getMessage():
            return False
        return True


# 应用过滤器到 werkzeug 日志
werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.addFilter(IgnoreHealthCheckFilter())

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "openvpn-webui-secret-key-change-me"
)

OPENVPN = os.environ.get("OPENVPN", "/etc/openvpn")


# 简单的认证装饰器
def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        username = os.environ.get("WEBUI_USERNAME", "admin")
        password = os.environ.get("WEBUI_PASSWORD", "openvpn")

        if not auth or auth.username != username or auth.password != password:
            response = jsonify({"error": "需要认证"})
            response.status_code = 401
            response.headers["WWW-Authenticate"] = 'Basic realm="OpenVPN Web UI"'
            return response
        return f(*args, **kwargs)

    return decorated


def run_command(cmd):
    """执行命令并返回结果"""
    try:
        logger.info(f"执行命令: {cmd}")
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        logger.info(f"命令返回码: {result.returncode}")
        if result.stdout:
            logger.info(f"命令输出: {result.stdout}")
        if result.stderr:
            logger.warning(f"命令错误: {result.stderr}")

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except Exception as e:
        logger.error(f"执行命令异常: {str(e)}")
        return {"success": False, "error": str(e)}


@app.route("/")
def index():
    """首页"""
    return render_template("index.html")


@app.route("/api/status")
def get_status():
    """获取系统状态"""
    status = {}

    # 获取当前模式
    env_file = f"{OPENVPN}/ovpn_env.sh"
    if os.path.exists(env_file):
        with open(env_file, "r") as f:
            content = f.read()
            # 更精确的匹配（检查 OVPN_GATEWAY_MODE="1" 或 =1）
            import re

            gateway_match = re.search(r'OVPN_GATEWAY_MODE[=\s]+"?1"?', content)
            ldap_match = re.search(r'OVPN_LDAP_ENABLED[=\s]+"?1"?', content)
            status["gateway_mode"] = bool(gateway_match)
            status["ldap_enabled"] = bool(ldap_match)
    else:
        status["gateway_mode"] = False
        status["ldap_enabled"] = False

    # 获取站点列表
    sites_dir = f"{OPENVPN}/sites"
    status["sites"] = []
    if os.path.exists(sites_dir):
        for info_file in os.listdir(sites_dir):
            if info_file.endswith(".info"):
                site_name = info_file.replace(".info", "")
                info_path = os.path.join(sites_dir, info_file)
                site_info = {}
                with open(info_path, "r") as f:
                    for line in f:
                        if "=" in line:
                            key, value = line.strip().split("=", 1)
                            site_info[key] = value

                # 检查连接状态
                pid_file = f"{OPENVPN}/site-pids/{site_name}.pid"
                if os.path.exists(pid_file):
                    with open(pid_file, "r") as f:
                        pid = f.read().strip()
                    try:
                        os.kill(int(pid), 0)
                        site_info["status"] = "running"
                    except:
                        site_info["status"] = "stopped"
                else:
                    site_info["status"] = "stopped"

                status["sites"].append(site_info)

    # 获取客户端列表
    pki_dir = f"{OPENVPN}/pki/issued"
    status["clients"] = []
    if os.path.exists(pki_dir):
        for cert_file in os.listdir(pki_dir):
            if cert_file.endswith(".crt"):
                client_name = cert_file.replace(".crt", "")
                cert_path = os.path.join(pki_dir, cert_file)
                mtime = os.path.getmtime(cert_path)

                # 获取证书过期时间
                expiry_date = None
                days_left = None
                try:
                    result = subprocess.run(
                        f"openssl x509 -in {cert_path} -noout -enddate",
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        # 解析输出: notAfter=Dec 19 10:30:00 2026 GMT
                        import re
                        from datetime import datetime as dt

                        match = re.search(r"notAfter=(.+)", result.stdout)
                        if match:
                            date_str = match.group(1).strip()
                            try:
                                # 解析日期：Dec 19 10:30:00 2026 GMT
                                expiry_dt = dt.strptime(
                                    date_str, "%b %d %H:%M:%S %Y %Z"
                                )
                                expiry_date = expiry_dt.strftime("%Y-%m-%d")
                                days_left = (expiry_dt - dt.now()).days
                            except ValueError:
                                try:
                                    # 尝试另一种格式
                                    expiry_dt = dt.strptime(
                                        date_str, "%b %d %H:%M:%S %Y GMT"
                                    )
                                    expiry_date = expiry_dt.strftime("%Y-%m-%d")
                                    days_left = (expiry_dt - dt.now()).days
                                except:
                                    expiry_date = date_str
                                    days_left = None
                except Exception as e:
                    logger.warning(f"获取证书 {client_name} 过期时间失败: {str(e)}")
                    expiry_date = None
                    days_left = None

                status["clients"].append(
                    {
                        "name": client_name,
                        "created": datetime.fromtimestamp(mtime).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "expiry_date": expiry_date,
                        "days_left": days_left,
                    }
                )

    return jsonify(status)


@app.route("/api/mode", methods=["GET", "POST"])
@require_auth
def manage_mode():
    """管理运行模式"""
    if request.method == "GET":
        env_file = f"{OPENVPN}/ovpn_env.sh"
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                content = f.read()
                gateway_mode = "OVPN_GATEWAY_MODE=1" in content
                return jsonify({"mode": "gateway" if gateway_mode else "normal"})
        return jsonify({"mode": "normal"})

    # POST - 切换模式
    data = request.json
    mode = data.get("mode", "normal")

    logger.info(f"切换模式请求: {mode}")

    result = run_command(f"ovpn_set_mode {mode}")
    if result["success"]:
        logger.info(f"模式切换成功: {mode}")
        return jsonify(
            {"message": f"已切换到{mode}模式，请重启服务使配置生效", "success": True}
        )
    else:
        error_msg = result.get("stderr") or result.get("error") or "切换失败"
        logger.error(f"模式切换失败: {error_msg}")
        return (
            jsonify(
                {
                    "error": error_msg,
                    "stdout": result.get("stdout", ""),
                    "success": False,
                }
            ),
            500,
        )


@app.route("/api/ldap", methods=["GET", "POST"])
@require_auth
def manage_ldap():
    """管理 LDAP 配置"""
    if request.method == "GET":
        ldap_conf = f"{OPENVPN}/ldap.conf"
        if os.path.exists(ldap_conf):
            config = {}
            with open(ldap_conf, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split(None, 1)
                        if len(parts) == 2:
                            config[parts[0].lower()] = parts[1]
            return jsonify(config)
        return jsonify({})

    # POST - 配置 LDAP
    data = request.json
    host = data.get("host", "")
    port = data.get("port", "389")
    base_dn = data.get("base_dn", "")
    bind_dn = data.get("bind_dn", "")
    bind_password = data.get("bind_password", "")
    filter_str = data.get("filter", "(&(objectClass=person)(uid=%u))")
    search_attr = data.get("search_attr", "uid")
    use_tls = data.get("use_tls", False)

    if not host or not base_dn:
        return jsonify({"error": "主机和Base DN是必需的", "success": False}), 400

    cmd = f'ovpn_config_ldap -h {host} -p {port} -b "{base_dn}"'
    if bind_dn:
        cmd += f' -D "{bind_dn}"'
    if bind_password:
        cmd += f' -w "{bind_password}"'
    if filter_str:
        cmd += f' -f "{filter_str}"'
    if search_attr:
        cmd += f" -s {search_attr}"
    if use_tls:
        cmd += " -S"

    result = run_command(cmd)
    if result["success"]:
        return jsonify({"message": "LDAP 配置成功", "success": True})
    else:
        return (
            jsonify({"error": result.get("stderr", "配置失败"), "success": False}),
            500,
        )


@app.route("/api/sites", methods=["GET", "POST", "DELETE"])
@require_auth
def manage_sites():
    """管理远程站点"""
    if request.method == "GET":
        sites_dir = f"{OPENVPN}/sites"
        sites = []
        if os.path.exists(sites_dir):
            for info_file in os.listdir(sites_dir):
                if info_file.endswith(".info"):
                    info_path = os.path.join(sites_dir, info_file)
                    site_info = {}
                    with open(info_path, "r") as f:
                        for line in f:
                            if "=" in line and not line.strip().startswith("#"):
                                key, value = line.strip().split("=", 1)
                                # 去除引号（兼容新旧格式）
                                value = value.strip('"').strip("'")
                                site_info[key] = value

                    # 检查是否已配置证书
                    conf_file = os.path.join(
                        sites_dir, f"{site_info.get('SITE_NAME', '')}.conf"
                    )
                    site_info["has_cert"] = False
                    site_info["expiry_date"] = None
                    site_info["days_left"] = None

                    if os.path.exists(conf_file):
                        with open(conf_file, "r") as f:
                            content = f.read()
                            site_info["has_cert"] = (
                                "<ca>" in content or "ca " in content
                            )

                            # 获取证书过期时间（从 <cert> 标签中）
                            if site_info["has_cert"]:
                                try:
                                    import re

                                    cert_match = re.search(
                                        r"<cert>(.*?)</cert>", content, re.DOTALL
                                    )
                                    if cert_match:
                                        cert_content = cert_match.group(1).strip()
                                        # 写入临时文件
                                        import tempfile

                                        with tempfile.NamedTemporaryFile(
                                            mode="w", suffix=".crt", delete=False
                                        ) as tmp:
                                            tmp.write(cert_content)
                                            tmp_path = tmp.name

                                        # 获取过期时间
                                        result = subprocess.run(
                                            f"openssl x509 -in {tmp_path} -noout -enddate",
                                            shell=True,
                                            capture_output=True,
                                            text=True,
                                            timeout=5,
                                        )
                                        os.unlink(tmp_path)

                                        if result.returncode == 0:
                                            from datetime import datetime as dt

                                            match = re.search(
                                                r"notAfter=(.+)", result.stdout
                                            )
                                            if match:
                                                date_str = match.group(1).strip()
                                                try:
                                                    expiry_dt = dt.strptime(
                                                        date_str,
                                                        "%b %d %H:%M:%S %Y GMT",
                                                    )
                                                    site_info["expiry_date"] = (
                                                        expiry_dt.strftime("%Y-%m-%d")
                                                    )
                                                    site_info["days_left"] = (
                                                        expiry_dt - dt.now()
                                                    ).days
                                                except:
                                                    site_info["expiry_date"] = date_str
                                except Exception as e:
                                    logger.warning(
                                        f"获取站点 {site_info.get('SITE_NAME', '')} 证书过期时间失败: {str(e)}"
                                    )

                    sites.append(site_info)
        return jsonify(sites)

    if request.method == "POST":
        # 添加站点
        data = request.json
        name = data.get("name", "")
        host = data.get("host", "")
        port = data.get("port", "1194")
        subnet = data.get("subnet", "")
        protocol = data.get("protocol", "udp")

        if not name or not host or not subnet:
            return (
                jsonify({"error": "站点名称、主机和子网是必需的", "success": False}),
                400,
            )

        cmd = f"ovpn_add_remote_site -n {name} -h {host} -p {port} -s {subnet} -P {protocol}"
        result = run_command(cmd)

        if result["success"]:
            return jsonify(
                {"message": f"站点 {name} 添加成功，请继续配置证书", "success": True}
            )
        else:
            return (
                jsonify({"error": result.get("stderr", "添加失败"), "success": False}),
                500,
            )

    if request.method == "DELETE":
        # 删除站点
        site_name = request.args.get("name")
        if not site_name:
            return jsonify({"error": "站点名称是必需的", "success": False}), 400

        logger.info(f"删除站点请求: {site_name}")

        sites_dir = f"{OPENVPN}/sites"
        deleted_files = []

        try:
            for ext in [".conf", ".info", ".key", ".crt", "-ca.crt"]:
                file_path = os.path.join(sites_dir, f"{site_name}{ext}")
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_files.append(f"{site_name}{ext}")
                    logger.info(f"已删除文件: {file_path}")

            if not deleted_files:
                logger.warning(f"站点 {site_name} 没有找到任何文件")
                return (
                    jsonify({"error": f"站点 {site_name} 不存在", "success": False}),
                    404,
                )

            # 停止站点连接进程
            logger.info(f"停止站点 {site_name} 的连接进程")
            pid_file = f"{OPENVPN}/site-pids/{site_name}.pid"
            if os.path.exists(pid_file):
                try:
                    with open(pid_file, "r") as f:
                        pid = f.read().strip()
                    run_command(f"kill {pid}")
                    os.remove(pid_file)
                    logger.info(f"已停止站点进程 PID: {pid}")
                except Exception as e:
                    logger.warning(f"停止进程失败: {str(e)}")

            # 更新路由配置
            logger.info(f"更新路由配置")
            result = run_command("ovpn_update_routes")
            if not result["success"]:
                logger.warning(f"更新路由失败: {result.get('stderr', '')}")

            logger.info(
                f"站点 {site_name} 删除成功，已删除: {', '.join(deleted_files)}"
            )

            # 提示用户重启服务
            message = f"""✅ 站点 {site_name} 删除成功！

已完成操作：
• 删除站点文件: {', '.join(deleted_files)}
• 停止站点连接进程
• 更新路由配置（已从 site-routes.conf 中移除）

⚠️ 重要：需要重启服务使配置生效
在服务器上执行: docker restart openvpn-gateway

💡 提示：
• 主 OpenVPN 服务器需要重启才能应用新路由
• 客户端需要重新连接
• 已连接的客户端不会自动更新路由"""

            return jsonify(
                {
                    "message": message,
                    "success": True,
                    "deleted_files": deleted_files,
                    "need_restart": True,
                }
            )
        except Exception as e:
            logger.error(f"删除站点 {site_name} 失败: {str(e)}")
            return jsonify({"error": f"删除失败: {str(e)}", "success": False}), 500


@app.route("/api/sites/<site_name>/cert", methods=["GET", "POST"])
@require_auth
def manage_site_cert(site_name):
    """管理站点证书"""
    sites_dir = f"{OPENVPN}/sites"
    conf_file = os.path.join(sites_dir, f"{site_name}.conf")

    if request.method == "GET":
        # 获取当前证书配置（不返回敏感内容，只返回是否已配置）
        if os.path.exists(conf_file):
            with open(conf_file, "r") as f:
                content = f.read()
                has_ca = "<ca>" in content or "ca " in content
                has_cert = "<cert>" in content or "cert " in content
                has_key = "<key>" in content or "key " in content
                has_tls = "<tls-auth>" in content or "tls-auth " in content

                return jsonify(
                    {
                        "has_ca": has_ca,
                        "has_cert": has_cert,
                        "has_key": has_key,
                        "has_tls": has_tls,
                        "configured": has_ca and has_cert and has_key,
                    }
                )
        return jsonify({"configured": False})

    if request.method == "POST":
        # 配置证书
        data = request.json
        ovpn_content = data.get("ovpn_content", "")

        if not ovpn_content:
            return jsonify({"error": "请提供 .ovpn 文件内容", "success": False}), 400

        if not os.path.exists(conf_file):
            return jsonify({"error": f"站点 {site_name} 不存在", "success": False}), 404

        try:
            # 提取证书内容
            import re

            # 提取各个证书部分
            ca_match = re.search(r"<ca>(.*?)</ca>", ovpn_content, re.DOTALL)
            cert_match = re.search(r"<cert>(.*?)</cert>", ovpn_content, re.DOTALL)
            key_match = re.search(r"<key>(.*?)</key>", ovpn_content, re.DOTALL)
            tls_match = re.search(
                r"<tls-auth>(.*?)</tls-auth>", ovpn_content, re.DOTALL
            )

            if not (ca_match and cert_match and key_match):
                return (
                    jsonify(
                        {
                            "error": "无法从 .ovpn 文件中提取证书，请确保包含 <ca>, <cert>, <key> 标签",
                            "success": False,
                        }
                    ),
                    400,
                )

            # 读取现有配置
            with open(conf_file, "r") as f:
                conf_content = f.read()

            # 移除旧的证书内容（如果有）
            conf_content = re.sub(r"<ca>.*?</ca>", "", conf_content, flags=re.DOTALL)
            conf_content = re.sub(
                r"<cert>.*?</cert>", "", conf_content, flags=re.DOTALL
            )
            conf_content = re.sub(r"<key>.*?</key>", "", conf_content, flags=re.DOTALL)
            conf_content = re.sub(
                r"<tls-auth>.*?</tls-auth>", "", conf_content, flags=re.DOTALL
            )
            conf_content = re.sub(r"key-direction \d+", "", conf_content)

            # 添加新的证书内容
            cert_block = "\n\n# 证书配置（自动添加）\n"
            cert_block += f"<ca>\n{ca_match.group(1).strip()}\n</ca>\n\n"
            cert_block += f"<cert>\n{cert_match.group(1).strip()}\n</cert>\n\n"
            cert_block += f"<key>\n{key_match.group(1).strip()}\n</key>\n"

            if tls_match:
                cert_block += (
                    f"\n<tls-auth>\n{tls_match.group(1).strip()}\n</tls-auth>\n"
                )
                cert_block += "key-direction 1\n"

            # 写入配置文件
            with open(conf_file, "w") as f:
                f.write(conf_content.strip() + cert_block)

            # 更新路由
            run_command("ovpn_update_routes")

            return jsonify(
                {
                    "message": f"站点 {site_name} 证书配置成功！请重启服务使配置生效。",
                    "success": True,
                }
            )

        except Exception as e:
            return jsonify({"error": f"配置证书失败: {str(e)}", "success": False}), 500


@app.route("/api/clients", methods=["GET", "POST", "DELETE"])
@require_auth
def manage_clients():
    """管理客户端证书"""
    if request.method == "GET":
        pki_dir = f"{OPENVPN}/pki/issued"
        clients = []
        if os.path.exists(pki_dir):
            for cert_file in os.listdir(pki_dir):
                if cert_file.endswith(".crt"):
                    client_name = cert_file.replace(".crt", "")
                    cert_path = os.path.join(pki_dir, cert_file)
                    mtime = os.path.getmtime(cert_path)

                    # 获取证书过期时间
                    expiry_date = None
                    days_left = None
                    try:
                        result = subprocess.run(
                            f"openssl x509 -in {cert_path} -noout -enddate",
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if result.returncode == 0:
                            import re
                            from datetime import datetime as dt

                            match = re.search(r"notAfter=(.+)", result.stdout)
                            if match:
                                date_str = match.group(1).strip()
                                try:
                                    expiry_dt = dt.strptime(
                                        date_str, "%b %d %H:%M:%S %Y GMT"
                                    )
                                    expiry_date = expiry_dt.strftime("%Y-%m-%d")
                                    days_left = (expiry_dt - dt.now()).days
                                except:
                                    expiry_date = date_str
                    except Exception as e:
                        logger.warning(
                            f"获取客户端 {client_name} 证书过期时间失败: {str(e)}"
                        )

                    clients.append(
                        {
                            "name": client_name,
                            "created": datetime.fromtimestamp(mtime).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                            "expiry_date": expiry_date,
                            "days_left": days_left,
                        }
                    )
        return jsonify(clients)

    if request.method == "POST":
        # 生成客户端证书
        data = request.json
        client_name = data.get("name", "")

        if not client_name:
            return jsonify({"error": "客户端名称是必需的", "success": False}), 400

        # 检查 vars 文件是否存在，不存在则创建
        vars_file = f"{OPENVPN}/vars"
        if not os.path.exists(vars_file):
            logger.warning(f"vars 文件不存在，正在创建: {vars_file}")
            try:
                with open(vars_file, "w") as f:
                    f.write(
                        f"""# EasyRSA Variables
# Minimal configuration for docker-openvpn-gateway

set_var EASYRSA_PKI "{OPENVPN}/pki"
"""
                    )
                logger.info(f"vars 文件已创建: {vars_file}")
            except Exception as e:
                logger.error(f"创建 vars 文件失败: {str(e)}")
                return (
                    jsonify({"error": f"创建配置文件失败: {str(e)}", "success": False}),
                    500,
                )

        # 默认使用 nopass 方式生成客户端证书
        # 如果 CA 有密码保护，会尝试使用 CA_PASSWORD 环境变量
        ca_password = os.environ.get("CA_PASSWORD", "")

        if ca_password:
            # CA 有密码保护，使用 expect 自动输入密码和确认
            logger.info(f"检测到 CA_PASSWORD，使用 expect 自动输入密码和确认")
            cmd = f"""expect << 'EOF'
set timeout 30
spawn easyrsa build-client-full {client_name} nopass
expect {{
    "Enter pass phrase*" {{
        send "{ca_password}\\r"
        exp_continue
    }}
    "Confirm requested details:*" {{
        send "yes\\r"
        exp_continue
    }}
    eof
}}
EOF"""
            result = run_command(cmd)
        else:
            # 尝试无密码方式（默认配置），使用 expect 自动确认
            logger.info(f"使用无密码方式生成客户端证书（自动确认）")
            cmd = f"""expect << 'EOF'
set timeout 30
spawn easyrsa build-client-full {client_name} nopass
expect {{
    "Confirm requested details:*" {{
        send "yes\\r"
        exp_continue
    }}
    eof
}}
EOF"""
            result = run_command(cmd)

            # 如果失败且提示需要密码，返回友好的错误信息
            if (
                not result["success"]
                and "pass phrase" in result.get("stderr", "").lower()
            ):
                logger.warning(f"CA 证书有密码保护但未设置 CA_PASSWORD")
                return (
                    jsonify(
                        {
                            "error": "CA 证书有密码保护，但未设置 CA_PASSWORD 环境变量",
                            "hint": "解决方案：\n1) 在 docker-compose.yml 中添加 CA_PASSWORD 环境变量\n2) 重新构建: docker-compose build\n3) 重启容器: docker restart openvpn-gateway\n\n或者重新初始化使用无密码CA（会删除现有证书）：\n1) docker exec -it openvpn-gateway ovpn_initpki nopass",
                            "success": False,
                        }
                    ),
                    500,
                )

        if result["success"]:
            logger.info(f"客户端 {client_name} 证书生成成功")
            return jsonify(
                {"message": f"客户端 {client_name} 证书生成成功", "success": True}
            )
        else:
            error_msg = result.get("stderr") or result.get("error") or "生成失败"
            logger.error(f"客户端证书生成失败: {error_msg}")
            return (
                jsonify(
                    {
                        "error": error_msg,
                        "stdout": result.get("stdout", ""),
                        "success": False,
                    }
                ),
                500,
            )

    if request.method == "DELETE":
        # 吊销客户端证书
        client_name = request.args.get("name")
        if not client_name:
            return jsonify({"error": "客户端名称是必需的", "success": False}), 400

        logger.info(f"吊销客户端证书: {client_name}")

        # 使用 expect 自动确认吊销
        cmd = f"""expect << 'EOF'
set timeout 30
spawn easyrsa revoke {client_name}
expect {{
    "Continue with revocation:*" {{
        send "yes\\r"
        exp_continue
    }}
    eof
}}
EOF"""

        result = run_command(cmd)

        if result["success"]:
            logger.info(f"证书吊销成功，生成 CRL")
            crl_result = run_command("easyrsa gen-crl")

            if crl_result["success"]:
                logger.info(f"客户端 {client_name} 证书已吊销并更新 CRL")
                return jsonify(
                    {
                        "message": f"✅ 客户端 {client_name} 证书已吊销\n\n已更新证书吊销列表（CRL）\n\n⚠️ 建议重启服务使吊销立即生效:\ndocker restart openvpn-gateway",
                        "success": True,
                    }
                )
            else:
                logger.warning(f"CRL 生成失败: {crl_result.get('stderr', '')}")
                return (
                    jsonify(
                        {
                            "message": f"证书已吊销，但 CRL 更新失败",
                            "error": crl_result.get("stderr", ""),
                            "success": False,
                        }
                    ),
                    500,
                )
        else:
            error_msg = result.get("stderr") or result.get("error") or "吊销失败"
            logger.error(f"吊销客户端 {client_name} 失败: {error_msg}")
            return (
                jsonify(
                    {
                        "error": error_msg,
                        "stdout": result.get("stdout", ""),
                        "success": False,
                    }
                ),
                500,
            )


@app.route("/api/clients/<client_name>/download")
@require_auth
def download_client_config(client_name):
    """下载客户端配置文件"""
    result = run_command(f"ovpn_getclient {client_name}")

    if result["success"]:
        config_content = result["stdout"]

        # 创建临时文件
        temp_file = f"/tmp/{client_name}.ovpn"
        with open(temp_file, "w") as f:
            f.write(config_content)

        return send_file(
            temp_file,
            as_attachment=True,
            download_name=f"{client_name}.ovpn",
            mimetype="application/x-openvpn-profile",
        )
    else:
        return jsonify({"error": "生成配置文件失败", "success": False}), 500


@app.route("/api/logs")
@require_auth
def get_logs():
    """获取日志"""
    log_type = request.args.get("type", "main")
    lines = request.args.get("lines", 100, type=int)

    if log_type == "main":
        # OpenVPN 主日志
        result = run_command(
            f'tail -n {lines} /var/log/openvpn.log 2>/dev/null || echo "日志文件不存在"'
        )
    else:
        # Site-to-Site 日志
        result = run_command(
            f'tail -n {lines} /var/log/openvpn-{log_type}.log 2>/dev/null || echo "日志文件不存在"'
        )

    return jsonify({"logs": result.get("stdout", ""), "success": True})


@app.route("/api/initialize", methods=["POST"])
@require_auth
def initialize():
    """初始化 OpenVPN"""
    data = request.json
    server_url = data.get("server_url", "")

    if not server_url:
        return jsonify({"error": "服务器 URL 是必需的", "success": False}), 400

    # 生成配置
    result = run_command(f"ovpn_genconfig -u {server_url}")
    if not result["success"]:
        return (
            jsonify(
                {"error": "生成配置失败: " + result.get("stderr", ""), "success": False}
            ),
            500,
        )

    return jsonify(
        {"message": "初始化成功，请手动运行 ovpn_initpki 初始化 PKI", "success": True}
    )


@app.route("/api/restart", methods=["POST"])
@require_auth
def restart_service():
    """重启服务提示（需要在容器外部执行）"""
    return jsonify(
        {
            "message": "请在宿主机上运行: docker restart openvpn-gateway",
            "success": True,
        }
    )


if __name__ == "__main__":
    # 监听所有网络接口
    app.run(host="0.0.0.0", port=8080, debug=False)
