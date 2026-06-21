# Refactor Result

## Date
2026-06-21

## Files Created

| File | Purpose |
|------|---------|
| `src/common.py` | Shared reusable logic — `load_ip_list()`, `login()`, `goto_lvd_page()`, `detect_checkbox_state()`, `save_result()`, plus constants (selectors, creds, timeout) |
| `src/check_lvd_status.py` | **Tool 1** — Read-only LVD status checker. Never modifies config. |
| `src/toggle_lvd_checkbox.py` | **Tool 2** — LVD checkbox toggle. Modifies only when 2nd arg is exactly `check`. |

## Files Modified

| File | Change |
|------|--------|
| `src/common.py` | Replaced stub/placeholders with real Playwright-based shared functions |
| `src/check_lvd_status.py` | Replaced broken markdown-laden stub with working read-only checker |

## Files Deleted

| File | Reason |
|------|--------|
| `edit_lvd_playwright.py` | Monolithic file; read + modify responsibilities now split into 2 tools |

## Summary of Changes

1. **Separation of concerns**: `edit_lvd_playwright.py` combined read + modify in one function. Now split into `check_lvd_status.py` (read-only) and `toggle_lvd_checkbox.py` (modify on explicit request).

2. **Shared code extracted** into `src/common.py`:
   - `load_ip_list(filename)` — reads CSV with PWR_NAME, IP columns
   - `login(page, ip)` — authenticates via Playwright using stored creds
   - `goto_lvd_page(page, ip)` — navigates to LVD config page
   - `detect_checkbox_state(page)` — reads checkbox without clicking
   - `save_result(results, filename, headers)` — writes CSV with custom headers
   - Constants: `USERNAME`, `PASSWORD`, `TIMEOUT`, `CHECKBOX_SELECTOR`, `ACCEPT_SELECTOR`

3. **Preserved** original login flow, selectors (`inputElement_un`, `inputElement_pw`, `formButton_submit`, `checkbox_1012_2040_0001`, `accept`), and Playwright patterns from original.

4. **Validation**:
   - All 3 files pass `py_compile` (syntax check)
   - `check_lvd_status.py`: zero write/tick/save calls — read-only verified
   - `toggle_lvd_checkbox.py`: checks `sys.argv[2] != "check"` before any device modification; prints usage and exits if missing/wrong

## CSV Output Schemas

### check_lvd_status.py
```
PWR_NAME, IP, LVD_Status, Result, Fail_Reason
POP001,192.168.1.10,Checked,OK,
POP002,192.168.1.11,Unchecked,OK,
POP003,192.168.1.12,,FAIL,Login Failed
```

### toggle_lvd_checkbox.py
```
PWR_NAME, IP, Action, Result, Fail_Reason
POP001,192.168.1.10,Already Checked,OK,
POP002,192.168.1.11,Checked,OK,
POP003,192.168.1.12,,FAIL,Navigation Error
```
