import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./card";
import { Button } from "./button";
import { Volume2, VolumeX, Globe, Moon, Sun } from "lucide-react";
import { useTheme } from "./theme-provider";

export function SettingsPage() {
  const { t, i18n } = useTranslation();
  const [volume, setVolume] = useState(80);
  const [isMuted, setIsMuted] = useState(false);
  const { theme, setTheme } = useTheme();
  const [language, setLanguage] = useState(i18n.language || "en");

  const languages = [
    { code: "en", name: "English" },
    { code: "es", name: "Español" },
    { code: "fr", name: "Français" },
    { code: "ja", name: "日本語" },
  ];

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newLang = e.target.value;
    setLanguage(newLang);
    i18n.changeLanguage(newLang);
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setVolume(parseInt(e.target.value));
    if (isMuted && parseInt(e.target.value) > 0) {
      setIsMuted(false);
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  const toggleDarkMode = () => {
    setTheme(theme === "dark" ? "light" : "dark");
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{t("settings.appearance")}</CardTitle>
          <CardDescription>{t("settings.appearanceDescription")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-sm font-medium">{t("settings.darkMode")}</h3>
              <p className="text-sm text-gray-500">{t("settings.darkModeDescription")}</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={toggleDarkMode}
              className="flex items-center gap-2 border-purple-200 dark:border-purple-800 hover:bg-purple-50 dark:hover:bg-purple-900/30"
            >
              {theme === "dark" ? (
                <>
                  <Sun className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                  <span className="text-purple-600 dark:text-purple-400">{t("settings.lightMode")}</span>
                </>
              ) : (
                <>
                  <Moon className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                  <span className="text-purple-600 dark:text-purple-400">{t("settings.darkMode")}</span>
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("settings.audio")}</CardTitle>
          <CardDescription>{t("settings.audioDescription")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="icon"
              onClick={toggleMute}
              aria-label={isMuted ? t("settings.unmute") : t("settings.mute")}
              className="border-purple-200 dark:border-purple-800 hover:bg-purple-50 dark:hover:bg-purple-900/30"
            >
              {isMuted ? (
                <VolumeX className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              ) : (
                <Volume2 className="h-4 w-4 text-purple-600 dark:text-purple-400" />
              )}
            </Button>
            <input
              type="range"
              min="0"
              max="100"
              value={isMuted ? 0 : volume}
              onChange={handleVolumeChange}
              className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
            />
            <span className="text-sm font-medium w-8 text-right">
              {isMuted ? 0 : volume}%
            </span>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("settings.language")}</CardTitle>
          <CardDescription>{t("settings.languageDescription")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-2">
            <Globe className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            <select
              value={language}
              onChange={handleLanguageChange}
              className="flex-1 rounded-md border border-gray-300 dark:border-gray-700 py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-transparent"
            >
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t("settings.about")}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-600">
            {t("settings.version")}: 1.0.0
          </p>
          <p className="text-sm text-gray-600 mt-1">
            {t("settings.copyright")} © {new Date().getFullYear()}
          </p>
        </CardContent>
      </Card>
    </div>
  );
} 