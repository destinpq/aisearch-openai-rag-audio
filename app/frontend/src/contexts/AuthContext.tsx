import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import axios from "axios";

interface User {
    username: string;
    role: string;
}

interface AuthContextType {
    user: User | null;
    token: string | null;
    login: (username: string, password: string) => Promise<boolean>;
    register: (username: string, password: string) => Promise<boolean>;
    logout: () => void;
    isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);

    // Set axios base URL from environment variable for production
    axios.defaults.baseURL = import.meta.env.VITE_API_URL;
    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) {
            axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
            // Decode token to get user info
            try {
                const payload = JSON.parse(atob(token.split(".")[1]));
                setUser({ username: payload.user_id, role: "user" });
            } catch (e) {
                localStorage.removeItem("token");
            }
        }
    }, []);

    const login = async (username: string, password: string): Promise<boolean> => {
        try {
            const response = await axios.post("/login", { username, password });
            const token = response.data.token;
            localStorage.setItem("token", token);
            axios.defaults.headers.common["Authorization"] = `Bearer ${token}`;
            const payload = JSON.parse(atob(token.split(".")[1]));
            setUser({ username: payload.user_id, role: "user" });
            return true;
        } catch (error) {
            return false;
        }
    };

    const register = async (username: string, password: string): Promise<boolean> => {
        try {
            await axios.post("/register", { username, password });
            return true;
        } catch (error) {
            return false;
        }
    };

    const logout = () => {
        localStorage.removeItem("token");
        delete axios.defaults.headers.common["Authorization"];
        setUser(null);
    };

    const value = {
        user,
        token: localStorage.getItem("token"),
        login,
        register,
        logout,
        isAuthenticated: !!user
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
