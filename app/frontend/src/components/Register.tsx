import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/contexts/AuthContext";

function Register() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();
    const { register } = useAuth();

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");
        const success = await register(username, password);
        if (success) {
            navigate("/login");
        } else {
            setError("Registration failed");
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
            <div className="max-w-md w-full space-y-8">
                <div className="text-center">
                    <h2 className="text-3xl font-bold text-gray-900">
                        Register
                    </h2>
                    <p className="mt-2 text-gray-600">
                        Create your account
                    </p>
                </div>
                <form className="mt-8 space-y-6" onSubmit={handleRegister}>
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="username" className="block text-sm font-medium text-gray-700">Username</label>
                            <input
                                id="username"
                                type="text"
                                value={username}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
                                placeholder="Enter your username"
                                required
                                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-700">Password</label>
                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                                placeholder="Enter your password"
                                required
                                className="mt-1 block w-full border-gray-300 rounded-md shadow-sm"
                            />
                        </div>
                    </div>
                    {error && <p className="text-red-500">{error}</p>}
                    <Button type="submit" className="w-full">
                        Register
                    </Button>
                </form>
                <div className="text-center">
                    <p className="text-sm text-gray-500">
                        Already have an account? <Link to="/login" className="text-blue-500">Login</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default Register;
