import React, { useState } from "react";
import { Form, Input, Button, Card, Typography, message } from "antd";
import { UserOutlined, LockOutlined } from "@ant-design/icons";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

const { Title, Text } = Typography;

interface LoginFormValues {
    username: string;
    password: string;
}

const LoginAntd: React.FC = () => {
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const onFinish = async (values: LoginFormValues) => {
        setLoading(true);
        try {
            const success = await login(values.username, values.password);
            if (success) {
                message.success("Login successful!");
                navigate("/app");
            } else {
                message.error("Login failed. Please check your credentials.");
            }
        } catch (error) {
            message.error("Login failed. Please check your credentials.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            style={{
                minHeight: "100vh",
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                padding: 20
            }}
        >
            <Card
                style={{
                    width: 400,
                    boxShadow: "0 20px 40px rgba(0,0,0,0.1)",
                    borderRadius: 16,
                    border: "none"
                }}
                bodyStyle={{ padding: "40px 32px" }}
            >
                <div style={{ textAlign: "center", marginBottom: 32 }}>
                    <div
                        style={{
                            width: 80,
                            height: 80,
                            background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                            borderRadius: "50%",
                            margin: "0 auto 16px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            fontSize: 32,
                            color: "white"
                        }}
                    >
                        🤖
                    </div>
                    <Title level={2} style={{ margin: 0 }}>
                        Welcome Back
                    </Title>
                    <Text type="secondary">Sign in to your AI PDF RAG account</Text>
                </div>

                <Form name="login" onFinish={onFinish} layout="vertical" size="large">
                    <Form.Item name="username" rules={[{ required: true, message: "Please input your username!" }]}>
                        <Input prefix={<UserOutlined />} placeholder="Username or email" style={{ borderRadius: 8 }} />
                    </Form.Item>

                    <Form.Item name="password" rules={[{ required: true, message: "Please input your password!" }]}>
                        <Input.Password prefix={<LockOutlined />} placeholder="Password" style={{ borderRadius: 8 }} />
                    </Form.Item>

                    <Form.Item>
                        <Button
                            type="primary"
                            htmlType="submit"
                            loading={loading}
                            block
                            style={{
                                height: 48,
                                borderRadius: 8,
                                background: "linear-gradient(135deg, #6366f1, #8b5cf6)",
                                border: "none",
                                fontSize: 16,
                                fontWeight: 600
                            }}
                        >
                            Sign In
                        </Button>
                    </Form.Item>
                </Form>

                <div style={{ textAlign: "center", marginTop: 24 }}>
                    <Text type="secondary">
                        Don't have an account?{" "}
                        <Link to="/register" style={{ color: "#6366f1", fontWeight: 600 }}>
                            Sign up here
                        </Link>
                    </Text>
                </div>
            </Card>
        </div>
    );
};

export default LoginAntd;
