# IPCam-Config-Tool

A browser-independent desktop utility designed to access, configure, and preview IP CCTV cameras directly using their IP addresses. 

## 🛑 The Problem Solved
Older IP cameras (especially **Hikvision** and other major brands) rely heavily on deprecated web browser components or **ActiveX/NPAPI preview plugins** (`WebComponents.exe`) to display live video streams and change settings. Because modern browsers (Chrome, Edge, Firefox) no longer support these plugins, users face severe issues where the camera page is completely inaccessible, or the live video preview area shows a broken plugin error / black screen.

**IPCam-Config-Tool** eliminates the need for any web browser. By entering the camera's IP address directly, you can manage manufacturer device configurations and view a stable live preview window natively inside this tool.

## ✨ Core Features
* **Direct IP Access:** Connect directly to any target camera by manually inputting its IP address and configuration credentials.
* **Plugin-Free Live Preview:** Bypasses broken browser plugins entirely, restoring the live camera feed view inside a native application frame.
* **Device Configuration:** Easily modify manufacturer-specific device settings and network parameters without opening a web browser.
* **Cross-Brand Support:** Focused heavily on resolving legacy Hikvision access issues, while remaining compatible with similar IP cameras.

## 🚀 How to Use the Executable
1. Navigate to the **[Releases](../../releases)** tab.
2. Download the latest compiled version (`IPCam-Config-Tool.v1.0.0.exe`).
3. Ensure your computer is on the same local network subnet as your cameras.
4. Launch the application, input your camera's IP address, port, and credentials to configure or preview the stream.

## ☕ Support This Project
If this application saved you from replacing a legacy CCTV camera or wasting hours fighting with old Internet Explorer plugins, consider supporting my open-source work!

* [❤️ Sponsor Me on GitHub](https://github.com/sponsors/Elangovan84)
