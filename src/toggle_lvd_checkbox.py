"""Tool 2 — LVD checkbox toggle (modify on explicit request only).

When the second CLI argument equals ``check``:
  - Login, navigate, detect state.
  - If already checked → report "Already Checked"; do nothing.
  - If unchecked      → check the box, save/apply, verify, report "Checked".

Otherwise prints usage and exits without touching any device.

Usage:
    python toggle_lvd_checkbox.py <input_file> check
"""
import sys
from playwright.sync_api import sync_playwright
from common import (
    load_ip_list,
    login,
    goto_lvd_page,
    detect_checkbox_state,
    save_result,
    CHECKBOX_SELECTOR,
    ACCEPT_SELECTOR,
    TIMEOUT,
)


def toggle_lvd_checkbox(pwr_name: str, ip: str) -> list[str]:
    """Check the LVD checkbox on one device (idempotent).

    Returns a row matching the CSV schema:
        [PWR_NAME, IP, Action, Result, Fail_Reason]
    """
    print(f"[*] Modifying LVD: {pwr_name} ({ip})")

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

            if state == "Checked":
                return [pwr_name, ip, "Already Checked", "OK", ""]

            # Unchecked → perform the action
            print(f"[+] Checking LVD checkbox for {pwr_name} ({ip})")
            page.check(CHECKBOX_SELECTOR)
            if page.is_visible(ACCEPT_SELECTOR, timeout=2000):
                page.click(ACCEPT_SELECTOR)
                page.wait_for_load_state("domcontentloaded", timeout=TIMEOUT)

            # Verify the change took effect
            verify_state, verify_error = detect_checkbox_state(page)
            if verify_state == "Checked":
                return [pwr_name, ip, "Checked", "OK", ""]
            else:
                reason = verify_error or "Verification failed after save"
                return [pwr_name, ip, "", "FAIL", reason]
        except Exception as e:
            return [pwr_name, ip, "", "FAIL", str(e)]
        finally:
            browser.close()


def main() -> None:
    if len(sys.argv) < 3 or sys.argv[2] != "check":
        print("Usage: python toggle_lvd_checkbox.py <input_file> check")
        print("  The second argument must be exactly 'check' to proceed.")
        print("  No devices were modified.")
        sys.exit(1)

    input_file = sys.argv[1]
    ip_list = load_ip_list(input_file)
    if not ip_list:
        print("[!] No devices to process.")
        sys.exit(1)

    results = [toggle_lvd_checkbox(pwr_name, ip) for pwr_name, ip in ip_list]
    output_file = f"{input_file}.result"
    save_result(results, output_file, ["PWR_NAME", "IP", "Action", "Result", "Fail_Reason"])


if __name__ == "__main__":
    main()
