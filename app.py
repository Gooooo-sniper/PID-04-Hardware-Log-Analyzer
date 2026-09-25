"""
IoT Dead Letter Queue (DLQ) Failure Analyzer (PID-04)
A Streamlit web application that analyzes crashed edge-device logs using
a Smart Rule-Based Parsing Engine to detect hardware failures.
"""

import streamlit as st
import re
from datetime import datetime
from dataclasses import dataclass
from typing import List, Optional
import uuid
import json


@dataclass
class HardwareSignature:
    """Represents a detectable hardware failure pattern"""
    name: str
    pattern: str  # Regex pattern
    component: str
    fix: str
    priority: int  # 1=Critical, 2=High, 3=Medium, 4=Low


# Hardware failure signatures database
HARDWARE_SIGNATURES = [
    # Critical Priority (1)
    HardwareSignature(
        name="Brownout Detection",
        pattern=r"(brownout|BOR|voltage drop|under.?voltage|supply voltage dropped)",
        component="Power Supply / Voltage Regulator",
        fix="Check power supply stability, add decoupling capacitors (100nF + 10uF), verify input voltage is within ESP32 spec (3.0-3.6V), inspect power traces for resistance",
        priority=1
    ),
    HardwareSignature(
        name="Watchdog Timer Reset",
        pattern=r"(watchdog|WDT|wdt reset|Task watchdog|watchdog triggered)",
        component="Firmware / RTOS Task Scheduling",
        fix="Identify blocking task, add watchdog resets in long loops, check for deadlocks, increase watchdog timeout if needed, review task priorities",
        priority=1
    ),
    HardwareSignature(
        name="Memory Allocation Failure",
        pattern=r"(heap|malloc failed|out of memory|OOM|allocation failed|heap.*exhausted)",
        component="Heap Memory Management",
        fix="Check for memory leaks, reduce buffer sizes, free unused memory, monitor heap fragmentation, consider using PSRAM, optimize data structures",
        priority=1
    ),
    HardwareSignature(
        name="Stack Overflow",
        pattern=r"(stack overflow|stackoverflow|stack canary|stack.*corruption)",
        component="Task Stack / Function Recursion",
        fix="Increase task stack size in xTaskCreate(), reduce local variable usage, check for deep recursion, review large arrays on stack, use heap allocation for large buffers",
        priority=1
    ),
    
    # High Priority (2)
    HardwareSignature(
        name="I2C Communication Timeout",
        pattern=r"(I2C.?TIMEOUT|i2c timeout|i2c bus error|I2C_ERROR|I2C.*failed)",
        component="I2C Bus / Connected Sensors",
        fix="Check pull-up resistors (4.7kΩ recommended), verify sensor connections and power, reduce I2C clock speed (try 100kHz), check for bus conflicts or address collisions",
        priority=2
    ),
    HardwareSignature(
        name="SPI Communication Failure",
        pattern=r"(SPI|spi_master|SPI transaction failed|spi error|SPI.*timeout)",
        component="SPI Bus / Peripheral Devices",
        fix="Verify SPI pin connections (MOSI, MISO, CLK, CS), check clock frequency compatibility, add delays between transactions, verify CS line behavior, check for signal integrity",
        priority=2
    ),
    HardwareSignature(
        name="Flash Memory Error",
        pattern=r"(flash|SPIFFS|partition|NVS|flash.*error|flash.*corrupt)",
        component="Flash Memory / File System",
        fix="Check flash wear leveling, verify partition table configuration, reformat SPIFFS/LittleFS, clear NVS with nvs_flash_erase(), consider factory reset, check for power issues during writes",
        priority=2
    ),
    
    # Medium Priority (3)
    HardwareSignature(
        name="Temperature Sensor Error",
        pattern=r"(temp sensor|temperature|DHT|DS18B20|sensor.*failed|sensor.*timeout)",
        component="Temperature Sensor (DHT22/DS18B20)",
        fix="Check sensor wiring and power supply, verify sensor I2C/1-Wire address, add pull-up resistor (4.7kΩ for DHT, 1-Wire), check timing requirements, replace faulty sensor",
        priority=3
    ),
    HardwareSignature(
        name="UART Communication Error",
        pattern=r"(UART|uart|serial timeout|rx buffer overflow|uart.*error)",
        component="UART / Serial Interface",
        fix="Check baud rate configuration matches both sides, verify TX/RX pin connections (not swapped), increase RX buffer size, add flow control if needed, check for data overrun",
        priority=3
    ),
    
    # Low Priority (4)
    HardwareSignature(
        name="WiFi Connection Failure",
        pattern=r"(WiFi|SSID|connection failed|wifi.*disconnect|wifi.*error)",
        component="WiFi Module / Network Stack",
        fix="Verify SSID and password configuration, check WiFi signal strength, increase connection timeout, verify router 2.4GHz band is enabled, check for channel congestion",
        priority=4
    ),
]


def setup_page_config():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="IoT DLQ Failure Analyzer",
        page_icon="🔧",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def display_header():
    """Render application title and description."""
    st.title("🔧 IoT Dead Letter Queue (DLQ) Failure Analyzer")
    st.markdown("""
    Analyze failed edge-device logs from your IoT DLQ using smart rule-based parsing.
    Detects hardware failures like Brownout, I2C Timeout, Watchdog Resets, and more.
    """)
    st.divider()


def generate_dlq_payload():
    """Generate simulated ESP32 hardware brownout log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    device_id = f"ESP32-{uuid.uuid4().hex[:8].upper()}"
    
    log = f"""[{timestamp}] [INFO] ESP32 Device Boot - ID: {device_id}
[{timestamp}] [INFO] Reset reason: Power-on reset
[{timestamp}] [INFO] ESP-IDF Version: v4.4.2
[{timestamp}] [INFO] Free heap: 295840 bytes
[{timestamp}] [INFO] PSRAM: 4194304 bytes
[{timestamp}] [INFO] Starting WiFi connection...
[{timestamp}] [INFO] Connected to SSID: IoT-Network-2.4GHz
[{timestamp}] [INFO] IP Address: 192.168.1.105
[{timestamp}] [INFO] Starting sensor readings...
[{timestamp}] [INFO] DHT22 initialized on GPIO 4
[{timestamp}] [INFO] I2C initialized: SDA=21, SCL=22
[{timestamp}] [WARN] Voltage fluctuation detected: 3.15V
[{timestamp}] [WARN] ADC reading unstable on VCC monitor
[{timestamp}] [ERROR] Brownout detector triggered
[{timestamp}] [ERROR] Supply voltage dropped below 3.0V threshold
[{timestamp}] [ERROR] Current voltage: 2.87V
[{timestamp}] [FATAL] System entering brownout reset sequence
[{timestamp}] [INFO] Saving crash data to NVS...
[{timestamp}] [INFO] Core dump started...

Guru Meditation Error: Core 0 panic'ed (Cache disabled but cached memory region accessed)

Core  0 register dump:
PC      : 0x400d1234  PS      : 0x00060330  A0      : 0x800d5678  A1      : 0x3ffb1234
A2      : 0x00000000  A3      : 0x3ffb5678  A4      : 0x00000001  A5      : 0x3ffc0000
A6      : 0x00000000  A7      : 0x00000000  A8      : 0x800d1234  A9      : 0x3ffb1200
A10     : 0x00000000  A11     : 0x3ffb5678  A12     : 0x00060320  A13     : 0x00060320

ELF file SHA256: a1b2c3d4e5f67890

Stack backtrace:
0x400d1234:0x3ffb1234 0x400d5678:0x3ffb5678 0x400d9abc:0x3ffb9abc 0x400e1234:0x3ffba234

[{timestamp}] [ERROR] Task watchdog: app_main task blocked for 15 seconds
[{timestamp}] [ERROR] Tasks currently running:
[{timestamp}] [ERROR]   IDLE0 (prio=0, stack=1024)
[{timestamp}] [ERROR]   main (prio=1, stack=4096) <-- BLOCKED
[{timestamp}] [FATAL] Restarting in 3 seconds due to BOR (Brownout Reset)
[{timestamp}] [INFO] Restart counter: 3
"""
    return log.strip()


def display_dlq_control_panel():
    """Render DLQ sidebar with fetch button and information."""
    st.header("📦 DLQ Control Panel")
    st.markdown("Simulate fetching failed payloads from your IoT Dead Letter Queue.")
    
    st.divider()
    
    # DLQ Fetch Button
    st.subheader("DLQ Simulator")
    if st.button("📥 Fetch Next Failed Payload from DLQ", type="primary", use_container_width=True):
        # Generate and store in session state
        dlq_log = generate_dlq_payload()
        st.session_state['log_content'] = dlq_log
        st.success("✅ Payload fetched from DLQ!")
        st.rerun()
    
    st.divider()
    
    # Status Information
    st.subheader("📊 DLQ Status")
    st.markdown(f"""
    - **Messages in DLQ:** 3
    - **Last Failure:** 2 minutes ago
    - **Device Type:** ESP32
    - **Failure Rate:** 0.8% (last 24h)
    """)
    
    st.divider()
    
    # About Section
    st.subheader("📖 About")
    st.markdown("""
    **Rule-Based Parser**  
    Detects 10+ hardware signatures:
    
    🔴 **Critical**
    - Brownout / Power Issues
    - Watchdog Resets
    - Memory Failures
    - Stack Overflow
    
    🟠 **High**
    - I2C Timeout
    - SPI Errors
    - Flash Corruption
    
    🟡 **Medium/Low**
    - Sensor Errors
    - UART Issues
    - WiFi Problems
    """)
    
    st.divider()
    
    st.subheader("🔧 Features")
    st.markdown("""
    ✓ No API keys required  
    ✓ Instant analysis (<2s)  
    ✓ Offline capable  
    ✓ Evidence-based diagnosis  
    ✓ Actionable fixes
    """)


def display_log_input():
    """Render log input text area and return content."""
    st.subheader("📋 System Log Input")
    
    # Get log from session state if available (from DLQ fetch)
    default_value = st.session_state.get('log_content', '')
    
    log_text = st.text_area(
        label="Paste your embedded system log here (or use 'Fetch from DLQ' button in sidebar):",
        value=default_value,
        height=300,
        placeholder="Example:\n[ERROR] Brownout detector triggered\n[ERROR] I2C timeout on bus 2\n[WARN] Temperature sensor unresponsive\n[FATAL] Watchdog reset triggered\n...",
        help="Paste raw log output from your ESP32, Arduino, or other embedded system."
    )
    
    return log_text.strip()


def analyze_log_with_rules(log_text: str) -> Optional[dict]:
    """
    Main rule-based parsing engine.
    Scans log for hardware failure signatures using pattern matching.
    
    Args:
        log_text: Raw log content to analyze
        
    Returns:
        Analysis result dict or None if no failure detected
    """
    if not log_text:
        return None
    
    # Sort signatures by priority (Critical first)
    sorted_signatures = sorted(HARDWARE_SIGNATURES, key=lambda x: x.priority)
    
    for signature in sorted_signatures:
        # Check if pattern matches anywhere in log (case-insensitive)
        if re.search(signature.pattern, log_text, re.IGNORECASE):
            # Extract evidence lines
            evidence_lines = extract_evidence(log_text, signature.pattern)
            
            # Format result
            result = format_analysis_result(signature, evidence_lines)
            return result
    
    # No signature matched
    return None


def extract_evidence(log_text: str, pattern: str) -> List[str]:
    """
    Extract log lines that match the given pattern.
    
    Args:
        log_text: Full log content
        pattern: Regex pattern to match
        
    Returns:
        List of matching log lines
    """
    evidence = []
    lines = log_text.split('\n')
    
    for line in lines:
        if re.search(pattern, line, re.IGNORECASE):
            evidence.append(line.strip())
    
    # Limit to first 5 matching lines to keep evidence concise
    return evidence[:5]


def format_analysis_result(signature: HardwareSignature, evidence: List[str]) -> dict:
    """
    Format analysis into the required 4-field output structure.
    
    Args:
        signature: Matched hardware signature
        evidence: List of log lines that matched
        
    Returns:
        Dictionary with 4 required fields
    """
    # Format evidence as bullet list
    evidence_text = "\n".join([f"• {line}" for line in evidence])
    if not evidence_text:
        evidence_text = "Pattern matched but no specific log lines extracted."
    
    # Add severity indicator
    priority_labels = {1: "🔴 CRITICAL", 2: "🟠 HIGH", 3: "🟡 MEDIUM", 4: "🟢 LOW"}
    severity = priority_labels.get(signature.priority, "UNKNOWN")
    
    return {
        "likely_failure": f"{signature.name} [{severity}]",
        "affected_component": signature.component,
        "supporting_evidence": evidence_text,
        "suggested_fix": signature.fix
    }


def display_analysis_results(data: dict):
    """
    Render analysis results in Streamlit UI using cards.
    
    Args:
        data: Analysis results with four required fields
    """
    st.subheader("📊 Analysis Results")
    st.success("✅ Analysis completed successfully!")
    
    # Create two columns for the top row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔴 Likely Failure")
        with st.container(border=True):
            st.markdown(data.get('likely_failure', 'N/A'))
    
    with col2:
        st.markdown("### ⚙️ Affected Component")
        with st.container(border=True):
            st.markdown(data.get('affected_component', 'N/A'))
    
    # Create two columns for the bottom row
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 📝 Supporting Evidence")
        with st.container(border=True):
            st.markdown(data.get('supporting_evidence', 'N/A'))
    
    with col4:
        st.markdown("### 🔧 Suggested Fix")
        with st.container(border=True):
            st.markdown(data.get('suggested_fix', 'N/A'))
    
    st.divider()
    
    # Discord Alert Button
    st.subheader("📢 Alert Dispatch")
    if st.button("📢 Dispatch Alert to Discord", type="secondary", use_container_width=True):
        simulate_discord_alert(data)


def simulate_discord_alert(data: dict):
    """
    Simulate Discord webhook alert dispatch.
    Displays formatted alert preview showing what would be sent.
    
    Args:
        data: Analysis results to include in alert
    """
    # Generate Discord webhook payload
    alert_payload = {
        "content": "🚨 **IoT Device Failure Alert**",
        "embeds": [{
            "title": "🔧 Hardware Failure Detected",
            "description": data["likely_failure"],
            "color": 15158332,  # Red color (#E74C3C)
            "fields": [
                {
                    "name": "⚙️ Affected Component",
                    "value": data["affected_component"],
                    "inline": False
                },
                {
                    "name": "📝 Evidence",
                    "value": data["supporting_evidence"][:300] + ("..." if len(data["supporting_evidence"]) > 300 else ""),
                    "inline": False
                },
                {
                    "name": "🔧 Suggested Fix",
                    "value": data["suggested_fix"][:300] + ("..." if len(data["suggested_fix"]) > 300 else ""),
                    "inline": False
                }
            ],
            "timestamp": datetime.now().isoformat(),
            "footer": {
                "text": "PID-04 IoT DLQ Failure Analyzer"
            }
        }]
    }
    
    # Display success message
    st.success("✅ Alert dispatched to Discord webhook successfully!")
    
    # Show alert preview
    with st.expander("📄 View Simulated Discord Alert Payload", expanded=True):
        st.json(alert_payload)
        st.info("""
        **Note:** This is a simulation. In production, this would POST to:  
        `https://discord.com/api/webhooks/{webhook_id}/{webhook_token}`
        
        To enable real Discord alerts:
        1. Create a Discord webhook in your server settings
        2. Add webhook URL to app configuration
        3. Uncomment Discord API integration code
        """)


def display_no_failure_result():
    """Display message when no hardware failure is detected."""
    st.info("✅ No hardware failure signatures detected in the log.")
    st.markdown("""
    The log has been analyzed against all known hardware failure patterns:
    - ✓ Power/Brownout issues
    - ✓ I2C/SPI communication errors
    - ✓ Watchdog resets
    - ✓ Memory failures
    - ✓ Sensor errors
    - ✓ WiFi/connectivity issues
    
    The log appears clean or contains failure types not yet in the signature database.
    """)


def analyze_and_display(log_text: str):
    """
    Orchestrate the log analysis and display results.
    
    Args:
        log_text: Raw log content to analyze
    """
    with st.spinner("🔍 Analyzing log with rule-based parser..."):
        # Run analysis
        result = analyze_log_with_rules(log_text)
        
        st.divider()
        
        if result:
            # Display results
            display_analysis_results(result)
        else:
            # No failure detected
            display_no_failure_result()


def main():
    """Main application entry point."""
    setup_page_config()
    display_header()
    
    # Sidebar: DLQ Control Panel
    with st.sidebar:
        display_dlq_control_panel()
    
    # Main area: Log input
    log_input = display_log_input()
    
    # Analyze button
    button_disabled = len(log_input) == 0
    button_help = "Enter log content above or fetch from DLQ to enable analysis" if button_disabled else "Click to analyze the log with rule-based parser"
    
    if st.button(
        "🔍 Analyze Log",
        disabled=button_disabled,
        help=button_help,
        type="primary",
        use_container_width=True
    ):
        analyze_and_display(log_input)
    
    # Footer
    st.divider()
    st.caption("PID-04 IoT DLQ Failure Analyzer | Smart Rule-Based Parsing Engine | No API Keys Required")


if __name__ == "__main__":
    main()
