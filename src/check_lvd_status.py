"""Tool 1 — Read-only LVD status checker.

Reads device list, logs in, navigates to LVD page, and reports current
checkbox state.  Never modifies configuration.

Usage:
    python check_lvd_status.py <input_file>
"""
import sys
from playwright.sync_api import sync_playwright
from common import load_ip_list, login, goto_lvd_page, detect_checkbox_state, save_result


def check_lvd_status(pwr_name: str, ip: str) -> list[str]:
    """Read-only check of LVD checkbox state on one device.

    Returns a row matching the CSV schema:
        [PWR_NAME, IP, LVD_Status, Result, Fail_Reason]
    """
    print(f"[*] Checking LVD status: {pwr_name} ({ip})")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            if not login(page, ip):
                return [pwr_name, ip, "", "FAIL", "Login Failed"]

            if not goto_lvd_page(page, ip):
                return [pwr_name, ip, "", "FAIL", "Navigation Error"]

            state, error = detect_checkbox_state(page)
            if state is None:
                return [pwr_name, ip, "", "FAIL", error]

            return [pwr_name, ip, state, "OK", ""]
        except Exception as e:
            return [pwr_name, ip, "", "FAIL", str(e)]
        finally:
            browser.close()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python check_lvd_status.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    ip_list = load_ip_list(input_file)
    if not ip_list:
        print("[!] No devices to process.")
        sys.exit(1)

    results = [check_lvd_status(pwr_name, ip) for pwr_name, ip in ip_list]
    output_file = f"{input_file}.result"
    save_result(results, output_file, ["PWR_NAME", "IP", "LVD_Status", "Result", "Fail_Reason"])


if __name__ == "__main__":
    main()
