#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OpenVPN Web 管理界面
提供简单易用的图形化配置和管理功能
"""

import os
import subprocess
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from functools import wraps

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
            return jsonify({"error": "需要认证"}), 401
        return f(*args, **kwargs)

    return decorated


def run_command(cmd):
    """执行命令并返回结果"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except Exception as e:
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
            status["gateway_mode"] = "1" in content and "OVPN_GATEWAY_MODE=1" in content
            status["ldap_enabled"] = "1" in content and "OVPN_LDAP_ENABLED=1" in content
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
                status["clients"].append(
                    {
                        "name": client_name,
                        "created": datetime.fromtimestamp(mtime).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
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

    result = run_command(f"ovpn_set_mode {mode}")
    if result["success"]:
        return jsonify({"message": f"已切换到{mode}模式", "success": True})
    else:
        return (
            jsonify({"error": result.get("stderr", "切换失败"), "success": False}),
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
                            if "=" in line:
                                key, value = line.strip().split("=", 1)
                                site_info[key] = value
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
            return jsonify({"message": f"站点 {name} 添加成功", "success": True})
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

        sites_dir = f"{OPENVPN}/sites"
        try:
            for ext in [".conf", ".info", ".key", ".crt", "-ca.crt"]:
                file_path = os.path.join(sites_dir, f"{site_name}{ext}")
                if os.path.exists(file_path):
                    os.remove(file_path)

            # 更新路由
            run_command("ovpn_update_routes")

            return jsonify({"message": f"站点 {site_name} 删除成功", "success": True})
        except Exception as e:
            return jsonify({"error": str(e), "success": False}), 500


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
                    clients.append(
                        {
                            "name": client_name,
                            "created": datetime.fromtimestamp(mtime).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            ),
                        }
                    )
        return jsonify(clients)

    if request.method == "POST":
        # 生成客户端证书
        data = request.json
        client_name = data.get("name", "")

        if not client_name:
            return jsonify({"error": "客户端名称是必需的", "success": False}), 400

        result = run_command(f"easyrsa build-client-full {client_name} nopass")

        if result["success"]:
            return jsonify(
                {"message": f"客户端 {client_name} 证书生成成功", "success": True}
            )
        else:
            return (
                jsonify({"error": result.get("stderr", "生成失败"), "success": False}),
                500,
            )

    if request.method == "DELETE":
        # 吊销客户端证书
        client_name = request.args.get("name")
        if not client_name:
            return jsonify({"error": "客户端名称是必需的", "success": False}), 400

        result = run_command(f"easyrsa revoke {client_name}")

        if result["success"]:
            run_command("easyrsa gen-crl")
            return jsonify(
                {"message": f"客户端 {client_name} 证书已吊销", "success": True}
            )
        else:
            return (
                jsonify({"error": result.get("stderr", "吊销失败"), "success": False}),
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
    """重启服务（需要在容器外部执行）"""
    return jsonify(
        {
            "message": "请在宿主机上运行: docker restart openvpn-container",
            "success": True,
        }
    )


if __name__ == "__main__":
    # 监听所有网络接口
    app.run(host="0.0.0.0", port=8080, debug=False)
