# IPCam-Config-Tool

A lightweight, browser-independent desktop application designed to discover, configure, and preview legacy IP CCTV cameras (including old Hikvision models).

## 🛑 The Problem Solved
Older IP cameras rely heavily on deprecated **Internet Explorer (IE) ActiveX plugins** (`WebComponents.exe`) to stream video and change advanced settings. Because modern web browsers (Chrome, Edge, Firefox) have completely dropped ActiveX/NPAPI support, users are often locked out of viewing their camera previews or managing settings. 

**IPCam-Config-Tool** bypasses the web interface entirely by interacting directly with the camera's hardware network protocols and streaming video over standard RTSP.

## ✨ Key Features
* **Zero Browser Dependency:** Modify network settings, IP addresses, and camera parameters without opening a browser.
* **Modern Live Preview:** Decodes the camera's raw video stream using modern rendering libraries instead of outdated plugins.
* **Device Auto-Discovery:** Scans your local network subnet to automatically detect connected IP cameras.

## 🚀 How to Use the Executable
1. Navigate to the **[Releases](../../releases)** section on the right side of this page.
2. Download the latest compiled version (`IPCam-Config-Tool.exe`).
3. Connect your computer to the same local network as your IP cameras.
4. Launch the application (Runs standalone, no installation required).

## 🛠️ Requirements & Technical Specs
* **Supported Protocols:** RTSP (Real-Time Streaming Protocol), UDP Device Discovery
* **Compatibility:** Tested extensively with legacy Hikvision and generic ONVIF-compliant IP cameras.
