import React, { useState } from "react";
import { Layout, Menu, Avatar, Dropdown, Button, Badge, Space, Typography, Switch } from "antd";
import {
    DashboardOutlined,
    AudioOutlined,
    FileTextOutlined,
    BarChartOutlined,
    UserOutlined,
    LogoutOutlined,
    BellOutlined,
    MenuFoldOutlined,
    MenuUnfoldOutlined,
    CrownOutlined,
    BulbOutlined
} from "@ant-design/icons";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext";

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

interface SupremeLayoutProps {
    children: React.ReactNode;
    darkMode?: boolean;
    setDarkMode?: (dark: boolean) => void;
}

const SupremeLayout: React.FC<SupremeLayoutProps> = ({ children, darkMode = false, setDarkMode }) => {
    const [collapsed, setCollapsed] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();
    const { user, logout } = useAuth();

    const menuItems = [
        {
            key: "/app",
            icon: <DashboardOutlined />,
            label: "Dashboard"
        },
        {
            key: "/upload",
            icon: <FileTextOutlined />,
            label: "Upload"
        },
        {
            key: "/analyze",
            icon: <BarChartOutlined />,
            label: "Analyze"
        },
        {
            key: "/enhanced-pdf",
            icon: <FileTextOutlined />,
            label: "Enhanced PDF"
        },
        {
            key: "/call",
            icon: <AudioOutlined />,
            label: "Voice Chat"
        },
        ...(user?.role === "admin"
            ? [
                  {
                      key: "/admin",
                      icon: <CrownOutlined />,
                      label: "Admin Panel"
                  }
              ]
            : [])
    ];

    const userMenuItems = [
        {
            key: "profile",
            icon: <UserOutlined />,
            label: "Profile",
            onClick: () => navigate("/profile")
        },
        {
            key: "logout",
            icon: <LogoutOutlined />,
            label: "Logout",
            onClick: logout
        }
    ];

    const handleMenuClick = ({ key }: { key: string }) => {
        navigate(key);
    };

    return (
        <Layout className="supreme-layout" style={{ minHeight: "100vh" }}>
            <Sider
                trigger={null}
                collapsible
                collapsed={collapsed}
                className="supreme-sider"
                theme="light"
                style={{
                    boxShadow: "2px 0 8px rgba(0,0,0,0.1)",
                    background: darkMode ? "#001529" : "#fff"
                }}
            >
                <div
                    className="supreme-logo"
                    style={{
                        height: 64,
                        margin: 16,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: collapsed ? "center" : "flex-start",
                        background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                        borderRadius: 8,
                        color: "white",
                        fontSize: collapsed ? 20 : 18,
                        fontWeight: "bold",
                        padding: collapsed ? 0 : "0 16px",
                        cursor: "pointer"
                    }}
                    onClick={() => navigate("/app")}
                >
                    {collapsed ? "AI" : "AI PDF RAG"}
                </div>

                <Menu
                    theme={darkMode ? "dark" : "light"}
                    mode="inline"
                    selectedKeys={[location.pathname]}
                    items={menuItems}
                    onClick={handleMenuClick}
                    style={{
                        border: "none",
                        background: "transparent"
                    }}
                />
            </Sider>

            <Layout>
                <Header
                    className="supreme-header"
                    style={{
                        padding: "0 24px",
                        background: darkMode ? "#141414" : "#fff",
                        borderBottom: `1px solid ${darkMode ? "#303030" : "#f0f0f0"}`,
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between"
                    }}
                >
                    <Space>
                        <Button
                            type="text"
                            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                            onClick={() => setCollapsed(!collapsed)}
                            style={{
                                fontSize: "16px",
                                width: 64,
                                height: 64
                            }}
                        />
                    </Space>

                    <Space size="large">
                        {setDarkMode && (
                            <Space>
                                <BulbOutlined />
                                <Switch checked={darkMode} onChange={setDarkMode} checkedChildren="🌙" unCheckedChildren="☀️" />
                            </Space>
                        )}

                        <Badge count={5} size="small">
                            <Button type="text" icon={<BellOutlined />} size="large" style={{ color: darkMode ? "#fff" : "#000" }} />
                        </Badge>

                        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight" arrow>
                            <Space style={{ cursor: "pointer" }}>
                                <Avatar
                                    size="large"
                                    icon={<UserOutlined />}
                                    style={{
                                        background: "linear-gradient(135deg, #6366f1, #8b5cf6)"
                                    }}
                                />
                                <div style={{ display: collapsed ? "none" : "block" }}>
                                    <Text strong style={{ color: darkMode ? "#fff" : "#000" }}>
                                        {user?.username || "User"}
                                    </Text>
                                    <br />
                                    <Text
                                        type="secondary"
                                        style={{
                                            fontSize: 12,
                                            color: darkMode ? "#888" : "#666"
                                        }}
                                    >
                                        Free Plan
                                    </Text>
                                </div>
                            </Space>
                        </Dropdown>
                    </Space>
                </Header>

                <Content
                    style={{
                        margin: "24px 16px",
                        padding: 24,
                        background: darkMode ? "#000" : "#f5f5f5",
                        borderRadius: 8,
                        overflow: "auto"
                    }}
                >
                    {children}
                </Content>
            </Layout>
        </Layout>
    );
};

export default SupremeLayout;
