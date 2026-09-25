# PID-04: IoT Dead Letter Queue (DLQ) Failure Analyzer

**A Streamlit web application that analyzes crashed edge-device logs using a Smart Rule-Based Parsing Engine.**

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 📋 Overview

The IoT DLQ Failure Analyzer helps embedded systems engineers quickly diagnose hardware failures in IoT edge devices (ESP32, Arduino, etc.) by analyzing system logs using pattern-matching rules. It simulates fetching failed payloads from a Dead Letter Queue (DLQ) and provides structured failure analysis with actionable fixes.

### Key Features

✅ **Smart Rule-Based Parsing Engine** - Detects 10+ hardware failure signatures  
✅ **DLQ Control Panel** - Simulate fetching failed ESP32 logs with one click  
✅ **No API Keys Required** - Fully offline, no cloud dependencies  
✅ **Instant Analysis** - Results in <2 seconds  
✅ **Evidence-Based Diagnosis** - Shows exact log lines that triggered detection  
✅ **Actionable Fixes** - Specific remediation steps for each failure type  
✅ **Discord Alert Simulation** - Preview webhook payloads for team notifications

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download this project**

```bash
cd PID-04
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the application**

```bash
streamlit run app.py
```

4. **Open your browser**

The app will automatically open at `http://localhost:8501`

---

## 🎯 Usage

### Method 1: Fetch from Simulated DLQ

1. Open the **DLQ Control Panel** in the left sidebar
2. Click **"Fetch Next Failed Payload from DLQ"**
3. A realistic ESP32 brownout log will auto-fill the text area
4. Click **"Analyze Log"** to detect the failure
5. View the 4-field analysis results
6. (Optional) Click **"Dispatch Alert to Discord"** to see the webhook preview

### Method 2: Manual Log Paste

1. Copy your embedded system log from your terminal or log file
2. Paste it into the **"System Log Input"** text area
3. Click **"Analyze Log"**
4. View the analysis results with supporting evidence

---

## 🔍 Detected Failure Signatures

The rule-based parser detects the following hardware failures:

### 🔴 Critical Priority
- **Brownout Detection** - Power supply voltage drops below threshold
- **Watchdog Timer Reset** - Task blocking or deadlock issues
- **Memory Allocation Failure** - Heap exhaustion or memory leaks
- **Stack Overflow** - Task stack too small or deep recursion

### 🟠 High Priority
- **I2C Communication Timeout** - Bus errors, missing pull-ups, or sensor issues
- **SPI Communication Failure** - Pin connection or timing issues
- **Flash Memory Error** - Wear leveling, corruption, or partition problems

### 🟡 Medium Priority
- **Temperature Sensor Error** - DHT22, DS18B20 connection or timing issues
- **UART Communication Error** - Baud rate or buffer overflow problems

### 🟢 Low Priority
- **WiFi Connection Failure** - SSID, password, or signal strength issues

---

## 📊 Output Format

The analyzer provides exactly **4 fields** for every detected failure:

1. **🔴 Likely Failure** - Description and severity level
2. **⚙️ Affected Component** - Specific hardware or firmware component
3. **📝 Supporting Evidence** - Actual log lines that matched the pattern
4. **🔧 Suggested Fix** - Step-by-step remediation instructions

---

## 🧪 Example Analysis

**Input Log:**
```
[2024-09-25 10:23:45] [ERROR] Brownout detector triggered
[2024-09-25 10:23:46] [ERROR] Supply voltage dropped below 3.0V
[2024-09-25 10:23:47] [FATAL] System entering brownout reset
```

**Output:**
- **Likely Failure:** Brownout Detection [🔴 CRITICAL]
- **Affected Component:** Power Supply / Voltage Regulator
- **Supporting Evidence:**
  - `[ERROR] Brownout detector triggered`
  - `[ERROR] Supply voltage dropped below 3.0V`
  - `[FATAL] System entering brownout reset`
- **Suggested Fix:** Check power supply stability, add decoupling capacitors (100nF + 10uF), verify input voltage is within ESP32 spec (3.0-3.6V), inspect power traces for resistance

---

## 🏗️ Architecture

### Component Layers

1. **UI Layer** - Streamlit widgets (sidebar, text area, cards, buttons)
2. **Simulation Layer** - DLQ payload generator and Discord alert formatter
3. **Smart Rule-Based Parser** - Pattern matching engine with priority-based detection
4. **Output Generator** - Formats analysis into 4-field structure

### How It Works

```
User Input → Rule-Based Parser → Pattern Matching → Evidence Extraction → 4-Field Output
```

The parser:
1. Scans log text with regex patterns (case-insensitive)
2. Matches against 10 predefined hardware signatures
3. Prioritizes by severity (Critical → High → Medium → Low)
4. Returns the highest priority match found
5. Extracts matching log lines as supporting evidence

---

## 🛠️ Customization

### Adding New Hardware Signatures

Edit `app.py` and add to the `HARDWARE_SIGNATURES` list:

```python
HARDWARE_SIGNATURES.append(
    HardwareSignature(
        name="Custom Failure Type",
        pattern=r"(keyword1|keyword2|error_code)",
        component="Component Name",
        fix="Detailed remediation steps",
        priority=2  # 1=Critical, 2=High, 3=Medium, 4=Low
    )
)
```

### Customizing DLQ Payloads

Modify the `generate_dlq_payload()` function to simulate different device types or failure scenarios.

---

## 📁 Project Structure

```
PID-04/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── .kiro/
    └── specs/
        └── PID-04/
            ├── requirements.md     # Detailed requirements (EARS notation)
            └── design.md           # Architecture and design documentation
```

---

## 🔐 Security & Privacy

- ✅ **No external API calls** - All processing happens locally
- ✅ **No data storage** - Logs are not saved or transmitted
- ✅ **No credentials required** - No API keys, tokens, or authentication
- ✅ **Offline capable** - Works without internet connection

---

## 🚢 Deployment

### Local Development
```bash
streamlit run app.py
```

### Streamlit Community Cloud
1. Push code to GitHub
2. Connect your repo at [share.streamlit.io](https://share.streamlit.io)
3. Deploy with one click (free tier available)

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
```

Build and run:
```bash
docker build -t pid-04-analyzer .
docker run -p 8501:8501 pid-04-analyzer
```

---

## 🧪 Testing

### Manual Testing Scenarios

1. **DLQ Fetch Test**
   - Click "Fetch Next Failed Payload from DLQ"
   - Verify ESP32 log appears in text area
   - Click "Analyze Log"
   - Should detect: Brownout Detection [CRITICAL]

2. **I2C Timeout Test**
   - Paste log containing "I2C timeout" or "I2C_TIMEOUT"
   - Should detect: I2C Communication Timeout [HIGH]

3. **Watchdog Test**
   - Paste log containing "watchdog" or "WDT reset"
   - Should detect: Watchdog Timer Reset [CRITICAL]

4. **Clean Log Test**
   - Paste log with no error keywords (e.g., only [INFO] entries)
   - Should display: "No hardware failure signatures detected"

5. **Discord Alert Test**
   - After analysis, click "Dispatch Alert to Discord"
   - Should show JSON payload preview

---

## 📖 Documentation

Detailed documentation available in `.kiro/specs/PID-04/`:

- **[requirements.md](../.kiro/specs/PID-04/requirements.md)** - Functional and non-functional requirements using EARS notation
- **[design.md](../.kiro/specs/PID-04/design.md)** - System architecture, data models, and component design

---

## 🔮 Future Enhancements

Potential features for future versions:

- [ ] Real DLQ integration (AWS SQS, Azure Service Bus, RabbitMQ)
- [ ] Actual Discord webhook integration
- [ ] Log file upload support
- [ ] Historical analysis and trend tracking
- [ ] Custom rule editor UI
- [ ] Machine learning-based anomaly detection
- [ ] Multi-device support (ESP8266, Arduino, Raspberry Pi)
- [ ] Real-time log streaming from edge devices
- [ ] Alert integrations (Slack, PagerDuty, Email, SMS)
- [ ] Dashboard with failure statistics
- [ ] Batch analysis for multiple logs
- [ ] PDF/Excel report export

---

## 🤝 Contributing

Contributions are welcome! To add new hardware signatures or improve detection accuracy:

1. Fork the repository
2. Add your signature to `HARDWARE_SIGNATURES` in `app.py`
3. Test with sample logs
4. Submit a pull request with description

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**PID-04 Development Team**

For questions or support, please open an issue in the repository.

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Designed for ESP32, Arduino, and embedded systems developers
- Inspired by real-world IoT edge device debugging challenges

---

## 📞 Support

If you encounter issues:

1. Check that Python 3.8+ is installed: `python --version`
2. Verify Streamlit installation: `streamlit --version`
3. Review the logs in the terminal for error messages
4. Ensure port 8501 is not in use by another application

**Common Issues:**

- **"Command not found: streamlit"** → Run `pip install streamlit`
- **"Port already in use"** → Stop other Streamlit apps or use `streamlit run app.py --server.port=8502`
- **"Module not found"** → Run `pip install -r requirements.txt`

---

**Happy Debugging! 🔧🚀**
