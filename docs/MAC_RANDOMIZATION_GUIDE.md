# 📱 MAC Address Randomization Guide

## 🚨 Important: Disable MAC Randomization for Reliable Tracking

Modern smartphones randomize MAC addresses for privacy. This affects tunnel tracking accuracy.

## 📱 iOS Devices (iPhone/iPad)

### Disable Private WiFi Address:
1. Open **Settings** app
2. Go to **WiFi**
3. Find your **Rajant/Tunnel WiFi network**
4. Tap the **(i)** icon next to network name
5. Turn **OFF** "Private WiFi Address"
6. Reconnect to the network

### Alternative Method:
1. **Settings** → **WiFi**
2. Tap **network name**
3. Toggle **Private WiFi Address** to **OFF**
4. Tap **Rejoin** when prompted

## 🤖 Android Devices

### Disable MAC Randomization:
1. Open **Settings** app
2. Go to **WiFi & internet** or **Connections**
3. Tap **WiFi**
4. Find your **Rajant/Tunnel WiFi network**
5. Tap **gear icon** or **network name**
6. Tap **Advanced** or **Privacy**
7. Change **Privacy** from "Use randomized MAC" to **"Use device MAC"**
8. Reconnect to network

### Samsung Devices:
1. **Settings** → **Connections** → **WiFi**
2. Tap **network name**
3. Tap **Advanced**
4. Set **MAC address type** to **"Phone MAC"**

## ⚠️ What Happens if NOT Disabled:

### Problem Symptoms:
- ❌ **You appear as "Unauthorized Device"** after some time
- ❌ **Tracking stops working** randomly  
- ❌ **New "unknown device" alerts** for your phone
- ❌ **Position history breaks** when MAC changes

### Technical Details:
- 📱 **iOS**: New MAC every 24-48 hours or network reconnect
- 🤖 **Android**: New MAC every reconnection or schedule
- 🔄 **Impact**: System sees you as new, unregistered device

## ✅ After Disabling MAC Randomization:

### Expected Behavior:
- ✅ **Consistent tracking** throughout tunnel work
- ✅ **Remains registered** as authorized worker
- ✅ **Accurate position history** 
- ✅ **No false security alerts**

## 🔐 Privacy Considerations:

### Tunnel Network Only:
- **Only disable** for work/tunnel WiFi networks
- **Keep enabled** for public WiFi (cafes, airports, etc.)
- **Your choice** - privacy vs. tracking accuracy

### Company Policy:
- Check with IT department about device policies
- Some companies may require specific settings
- Alternative identification methods may be available

## 🧪 Testing Steps:

1. **Register** in worker app with MAC randomization OFF
2. **Disconnect** and reconnect to Rajant WiFi
3. **Verify** you still appear as registered worker
4. **Move between** tunnel sections
5. **Confirm** continuous tracking without interruption

## 🆘 Troubleshooting:

### Still Having Issues?
- **Check** WiFi network name is correct
- **Verify** setting was applied (restart phone if needed)
- **Re-register** in worker app after changing setting
- **Contact** tunnel safety coordinator for assistance

### Alternative Solutions:
- Some systems can track multiple MACs per person
- Backup identification methods may be available
- Check with your safety coordinator

---

**⚠️ Important: This setting only affects tunnel WiFi tracking accuracy. Your device privacy on other networks remains protected.** 