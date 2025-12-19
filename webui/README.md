# Web UI 更新说明

## 新功能：直接在 Web UI 中配置站点证书

### 特性

- ✅ 无需 SSH 进容器
- ✅ 图形化证书配置界面
- ✅ 自动解析 .ovpn 文件
- ✅ 自动提取证书、密钥等信息
- ✅ 一键保存配置
- ✅ 显示证书配置状态

### API 端点

#### GET /api/sites/<site_name>/cert
获取站点证书配置状态

**响应**:
```json
{
  "has_ca": true,
  "has_cert": true,
  "has_key": true,
  "has_tls": true,
  "configured": true
}
```

#### POST /api/sites/<site_name>/cert
配置站点证书

**请求**:
```json
{
  "ovpn_content": "client\ndev tun\n...\n<ca>...</ca>\n<cert>...</cert>..."
}
```

**响应**:
```json
{
  "success": true,
  "message": "站点 huawei 证书配置成功！"
}
```

### 使用流程

1. 添加站点
2. 点击"配置证书"按钮
3. 粘贴 .ovpn 文件内容
4. 保存
5. 重启服务

### 技术实现

- 使用正则表达式提取证书内容
- 自动处理 `<ca>`, `<cert>`, `<key>`, `<tls-auth>` 标签
- 自动设置 `key-direction`
- 验证证书完整性
- 更新路由配置

