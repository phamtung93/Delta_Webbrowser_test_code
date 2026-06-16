from playwright.sync_api import sync_playwright
import csv

#  File chứa danh sách IP
INPUT_FILE = "ip_list.txt"
OUTPUT_FILE = "ip_result.txt"

USERNAME = "Admin"
PASSWORD = "adminTps"

TIMEOUT = 5000  # 5 giây timeout


def load_ip_list(filename):
    """ Đọc danh sách IP từ file với format mới """
    ip_list = []
    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Bỏ dòng tiêu đề (PWR_NAME, IP)
        for row in reader:
            if len(row) >= 2:  # Định dạng phải có ít nhất 2 cột: PWR_NAME, IP
                pwr_name = row[0].strip()
                ip = row[1].strip()
                ip_list.append((pwr_name, ip))
    return ip_list


def save_result(results, filename):
    """ Ghi kết quả vào file """
    with open(filename, "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["PWR_NAME", "IP", "Status", "Fail_Reason"])
        writer.writerows(results)


def edit_lvd(pwr_name, ip):
    """ Tự động đăng nhập và chỉnh LVD trên thiết bị với IP chỉ định """
    print(f"[*] Đang xử lý: {pwr_name} ({ip})")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Chạy headless để tăng tốc
        page = browser.new_page()

        login_url = f"http://{ip}/controller/login"
        lvd_url = f"http://{ip}/controller/control/lvd"

        try:
            # Truy cập trang login với timeout = 5s
            page.goto(login_url, wait_until="domcontentloaded", timeout=TIMEOUT)
            print(f"[+] Đã vào trang đăng nhập của {pwr_name} ({ip})")

            # Kiểm tra xem input username có hiển thị không trước khi fill
            if page.is_visible('input[name="inputElement_un"]', timeout=2000):
                page.fill('input[name="inputElement_un"]', USERNAME)
                page.fill('input[name="inputElement_pw"]', PASSWORD)
                page.click('input[name="formButton_submit"]')

                # Chờ load trang sau login (giảm timeout)
                page.wait_for_load_state("domcontentloaded", timeout=TIMEOUT)
                print(f"[+] Đăng nhập thành công vào {pwr_name} ({ip})")
            else:
                print(f"[] Không tìm thấy ô nhập username trên {pwr_name} ({ip}). Bỏ qua!")
                return [pwr_name, ip, "FAILED", "Login page not loaded"]

            # Truy cập trang LVD với timeout = 5s
            page.goto(lvd_url, wait_until="domcontentloaded", timeout=TIMEOUT)

            # Kiểm tra checkbox LVD
            checkbox_selector = 'input[name="checkbox_1012_2040_0001"]'
            if page.is_visible(checkbox_selector, timeout=2000):
                print(f"[+] Checkbox LVD tồn tại trên {pwr_name} ({ip}), tiến hành chỉnh sửa...")
                page.check(checkbox_selector)
                page.click('input[name="accept"]')

                # Reload lại trang để kiểm tra thay đổi
                page.reload(timeout=TIMEOUT)
                page.wait_for_load_state("domcontentloaded", timeout=TIMEOUT)

                # Kiểm tra lại checkbox đã được tick chưa
                if page.is_checked(checkbox_selector):
                    print(f"[] Chỉnh LVD thành công trên {pwr_name} ({ip})!")
                    return [pwr_name, ip, "OK", ""]
                else:
                    print(f"[] Chỉnh LVD thất bại trên {pwr_name} ({ip}).")
                    return [pwr_name, ip, "FAILED", "Checkbox not applied"]
            else:
                print(f"[] Không tìm thấy checkbox LVD trên {pwr_name} ({ip}).")
                return [pwr_name, ip, "FAILED", "Checkbox not found"]

        except Exception as e:
            print(f"[] Lỗi khi truy cập {pwr_name} ({ip}): {e}")
            return [pwr_name, ip, "FAILED", str(e)]

        finally:
            browser.close()


if __name__ == "__main__":
    ip_list = load_ip_list(INPUT_FILE)
    results = []

    for pwr_name, ip in ip_list:
        result = edit_lvd(pwr_name, ip)
        results.append(result)

    save_result(results, OUTPUT_FILE)
    print(f"\n Kết quả đã lưu vào {OUTPUT_FILE}")

