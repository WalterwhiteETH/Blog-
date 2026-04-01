import { DeviceClass } from '/@/renderer/api/client';

const lowEndUserAgentPattern = /(tecno|itel|android go|low-end android)/i;

export const detectDeviceClass = (): DeviceClass => {
    const userAgent = navigator.userAgent || '';
    const deviceMemory = (navigator as any).deviceMemory as number | undefined;

    if ((deviceMemory && deviceMemory < 4) || lowEndUserAgentPattern.test(userAgent)) {
        return 'lite';
    }

    return 'high';
};
