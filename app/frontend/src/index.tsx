import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";

import { I18nextProvider } from "react-i18next";
import i18next from "./i18n/config";

import { AuthProvider } from "./contexts/AuthContext";
import App from "./App.tsx";
import "./index.css";

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <BrowserRouter>
            <I18nextProvider i18n={i18next}>
                <AuthProvider>
                    <App />
                </AuthProvider>
            </I18nextProvider>
        </BrowserRouter>
    </StrictMode>
);
