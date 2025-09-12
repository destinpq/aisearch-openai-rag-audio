import { Wifi, WifiOff } from "lucide-react";
// import { useTranslation } from "react-i18next";

import useInternetSpeed from "@/hooks/useInternetSpeed";

const InternetSpeedIndicator = () => {
    const { internetSpeed } = useInternetSpeed();
    // const { t } = useTranslation();

    const getQualityColor = (quality: string) => {
        switch (quality) {
            case 'Excellent':
                return 'text-green-600';
            case 'Good':
                return 'text-blue-600';
            case 'Poor':
                return 'text-orange-600';
            case 'Very Poor':
                return 'text-red-600';
            default:
                return 'text-gray-600';
        }
    };

    const getSpeedColor = (quality: string) => {
        switch (quality) {
            case 'Excellent':
                return 'text-green-500';
            case 'Good':
                return 'text-blue-500';
            case 'Poor':
                return 'text-orange-500';
            case 'Very Poor':
                return 'text-red-500';
            default:
                return 'text-gray-500';
        }
    };

    const getWifiIcon = (quality: string) => {
        if (quality === 'Very Poor' && internetSpeed.speed === 0) {
            return <WifiOff className="h-4 w-4" />;
        }
        return <Wifi className="h-4 w-4" />;
    };

    if (internetSpeed.isLoading) {
        return (
            <div className="flex flex-col items-center justify-center p-2 bg-gray-50 rounded-lg border">
                <div className="flex items-center space-x-1 text-gray-600">
                    <Wifi className="h-4 w-4 animate-pulse" />
                    <span className="text-sm font-medium">Testing Connection</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                    Measuring network quality...
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center justify-center p-3 bg-white rounded-lg border shadow-sm mb-4">
            <div className={`flex items-center space-x-2 ${getQualityColor(internetSpeed.quality)}`}>
                {getWifiIcon(internetSpeed.quality)}
                <span className="text-sm font-semibold">
                    {internetSpeed.quality}
                </span>
            </div>
            <div className={`text-xs mt-1 font-medium ${getSpeedColor(internetSpeed.quality)}`}>
                {internetSpeed.speed === 0 ? 'Offline' : `${internetSpeed.speed} Mbps`}
            </div>
        </div>
    );
};

export default InternetSpeedIndicator; 