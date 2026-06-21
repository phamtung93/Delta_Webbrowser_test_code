import csv
import os
from playwright.sync_api import Page

USERNAME = "Admin"
PASSWORD = "adminTps"
TIMEOUT = 5000
CHECKBOX_SELECTOR = 'input[name="checkbox_1012_2040_0001"]'
ACCEPT_SELECTOR = 'input[name="accept"]'


def load_ip_list(filename: str) -> list[tuple[str, str]]:
    """Read device list from CSV with columns: PWR_NAME, IP.

    Returns list of (pwr_name, ip) tuples.  Empty list on missing file.
    """
    ip_list: list[tuple[str, str]] = []
    if not os.path.exists(filename):
        print(f"[!] File not found: {filename}")
        return ip_list
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        for row in reader:
            if len(row) >= 2:
                pwr_name = row[0].strip()
                ip = row[1].strip()
                ip_list.append((pwr_name, ip))
    return ip_list


def login(page: Page, ip: str) -> bool:
    """Authenticate on the device at *ip*.  Returns True on success."""
    login_url = f"http://{ip}/controller/login"
    try:
        page.goto(login_url, wait_until="domcontentloaded", timeout=TIMEOUT)
        if not page.is_visible('input[name="inputElement_un"]', timeout=2000):
            return False
        page.fill('input[name="inputElement_un"]', USERNAME)
        page.fill('input[name="inputElement_pw"]', PASSWORD)
        page.click('input[name="formButton_submit"]')
        page.wait_for_load_state("domcontentloaded", timeout=TIMEOUT)
        return True
    except Exception:
        return False


def goto_lvd_page(page: Page, ip: str) -> bool:
    """Navigate to the LVD configuration page.  Returns True on success."""
    lvd_url = f"http://{ip}/controller/control/lvd"
    try:
        page.goto(lvd_url, wait_until="domcontentloaded", timeout=TIMEOUT)
        return True
    except Exception:
        return False


def detect_checkbox_state(page: Page) -> tuple[str | None, str]:
    """Read the LVD checkbox state without modifying it.

    Returns (state_label, error_message) where *state_label* is one of:
        "Checked" / "Unchecked" / None  (None + error message on failure).
    """
    try:
        if not page.is_visible(CHECKBOX_SELECTOR, timeout=2000):
            return None, "Checkbox not found"
        is_checked = page.is_checked(CHECKBOX_SELECTOR)
        return ("Checked" if is_checked else "Unchecked"), ""
    except Exception as e:
        return None, str(e)


def save_result(results: list[list[str]], filename: str, headers: list[str]) -> None:
    """Write *results* to a CSV file with the given *headers*."""
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(results)
    print(f"[+] Results saved to {filename}")
