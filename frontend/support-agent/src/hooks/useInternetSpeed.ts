import { useState, useEffect, useCallback } from 'react';

export interface InternetSpeed {
    speed: number; // in Mbps
    quality: 'Very Poor' | 'Poor' | 'Good' | 'Excellent';
    isLoading: boolean;
}

const useInternetSpeed = () => {
    const [internetSpeed, setInternetSpeed] = useState<InternetSpeed>({
        speed: 0,
        quality: 'Poor',
        isLoading: true
    });

    const getQualityFromSpeed = (speed: number): InternetSpeed['quality'] => {
        if (speed < 1) return 'Very Poor';
        if (speed < 5) return 'Poor';
        if (speed < 25) return 'Good';
        return 'Excellent';
    };

    const measureLatency = useCallback(async (): Promise<number> => {
        try {
            const measurements: number[] = [];
            const testEndpoints = [
                '/', // Current domain
                '/favicon.ico', // Common endpoint
                window.location.origin + '/health' // Health check if available
            ];

            for (const endpoint of testEndpoints) {
                try {
                    const startTime = performance.now();
                    await fetch(endpoint, {
                        method: 'HEAD',
                        cache: 'no-cache',
                        mode: 'same-origin'
                    });
                    const endTime = performance.now();
                    measurements.push(endTime - startTime);
                } catch (error) {
                    // Skip failed endpoints
                    continue;
                }
            }

            if (measurements.length === 0) {
                throw new Error('All latency tests failed');
            }

            // Return average latency
            return measurements.reduce((sum, latency) => sum + latency, 0) / measurements.length;
        } catch (error) {
            console.warn('Latency test failed:', error);
            return 1000; // Default to high latency
        }
    }, []);

    const getConnectionSpeed = useCallback((): number => {
        // @ts-ignore - navigator.connection is not in TypeScript definitions
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        
        if (connection && connection.downlink) {
            return connection.downlink; // Returns speed in Mbps
        }
        
        return 0;
    }, []);

    const getEffectiveType = useCallback((): string => {
        // @ts-ignore - navigator.connection is not in TypeScript definitions
        const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        return connection?.effectiveType || 'unknown';
    }, []);

    const measureSpeed = useCallback(async () => {
        setInternetSpeed(prev => ({ ...prev, isLoading: true }));
        
        try {
            let speed = 0;
            let quality: InternetSpeed['quality'] = 'Poor';
            
            // Method 1: Try to get speed from connection API
            const connectionSpeed = getConnectionSpeed();
            const effectiveType = getEffectiveType();
            
            if (connectionSpeed > 0) {
                speed = connectionSpeed;
            } else {
                // Method 2: Estimate based on effective connection type
                switch (effectiveType) {
                    case '4g':
                        speed = 50; // Estimate for 4G
                        break;
                    case '3g':
                        speed = 8; // Estimate for 3G
                        break;
                    case '2g':
                        speed = 0.5; // Estimate for 2G
                        break;
                    case 'slow-2g':
                        speed = 0.1; // Estimate for slow 2G
                        break;
                    default:
                        // Method 3: Use latency-based estimation
                        const latency = await measureLatency();
                        
                        // Convert latency to estimated speed (inverse relationship)
                        if (latency < 20) {
                            speed = 100; // Excellent - very low latency
                        } else if (latency < 50) {
                            speed = 50; // Excellent - low latency
                        } else if (latency < 100) {
                            speed = 25; // Good - moderate latency
                        } else if (latency < 300) {
                            speed = 5; // Poor - high latency
                        } else {
                            speed = 1; // Very Poor - very high latency
                        }
                        break;
                }
            }
            
            // Additional checks for offline status
            if (!navigator.onLine) {
                speed = 0;
            }
            
            quality = getQualityFromSpeed(speed);
            
            setInternetSpeed({
                speed: Math.round(speed * 10) / 10,
                quality,
                isLoading: false
            });
            
        } catch (error) {
            console.error('Speed measurement failed:', error);
            setInternetSpeed({
                speed: 0,
                quality: 'Very Poor',
                isLoading: false
            });
        }
    }, [measureLatency, getConnectionSpeed, getEffectiveType]);

    useEffect(() => {
        // Initial measurement
        measureSpeed();
        
        // Set up periodic measurements every 30 seconds
        const interval = setInterval(measureSpeed, 30000);
        
        // Listen for online/offline events
        const handleOnline = () => measureSpeed();
        const handleOffline = () => {
            setInternetSpeed({
                speed: 0,
                quality: 'Very Poor',
                isLoading: false
            });
        };
        
        window.addEventListener('online', handleOnline);
        window.addEventListener('offline', handleOffline);
        
        return () => {
            clearInterval(interval);
            window.removeEventListener('online', handleOnline);
            window.removeEventListener('offline', handleOffline);
        };
    }, [measureSpeed]);

    return { internetSpeed, refreshSpeed: measureSpeed };
};

export default useInternetSpeed; 