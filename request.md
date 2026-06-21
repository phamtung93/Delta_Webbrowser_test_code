# TASK: Refactor LVD Tool

You must modify the existing project source code.

Read the current implementation first and identify all files related to:

- edit_lvd
- LVD page navigation
- login workflow
- CSV export
- common utilities

Then perform the refactor described below.

---

# Objective

Split the current LVD functionality into two completely independent tools.

The current implementation mixes:

1. Reading/checking LVD status.
2. Modifying LVD checkbox state.

These responsibilities must be separated.

---

# Tool 1: check_lvd_status.py

## Purpose

Read device list and only check current LVD status.

## Behavior

- Read devices from input file.
- Login to device.
- Navigate to LVD page.
- Detect current checkbox state.
- Never modify configuration.
- Never click checkbox.
- Never save/apply.

## Output CSV

Columns:

PWR_NAME
IP
LVD_Status
Result
Fail_Reason

Example:

POP001,192.168.1.10,Checked,OK,
POP002,192.168.1.11,Unchecked,OK,
POP003,192.168.1.12,,FAIL,Login Failed

---

# Tool 2: toggle_lvd_checkbox.py

## Purpose

Modify LVD only when explicitly requested.

## Command Line

python toggle_lvd_checkbox.py ip_list.txt check

## Behavior

When second argument equals:

check

- Login device.
- Navigate to LVD page.
- Detect checkbox state.

If already checked:

- Do not change configuration.
- Report "Already Checked".

If unchecked:

- Check checkbox.
- Save/apply if required.
- Report "Checked".

If second argument is missing or not equal to "check":

- Exit immediately.
- Print usage/help message.
- Do not modify any device.

Example invalid commands:

python toggle_lvd_checkbox.py ip_list.txt

python toggle_lvd_checkbox.py ip_list.txt abc

---

# Output CSV

Columns:

PWR_NAME
IP
Action
Result
Fail_Reason

Example:

POP001,192.168.1.10,Already Checked,OK,
POP002,192.168.1.11,Checked,OK,
POP003,192.168.1.12,,FAIL,Navigation Error

---

# Shared Code

Move reusable logic into common.py

Reuse:

- load_ip_list()
- login()
- goto_lvd_page()
- save_result()

Avoid duplicated code.

---

# Project Structure

check_lvd_status.py

toggle_lvd_checkbox.py

common.py

---

# Requirements

- Generate complete working code.
- Update command line parsing.
- Update CSV export logic.
- Preserve existing selectors.
- Preserve existing login workflow.
- Preserve existing Playwright workflow.
- Remove old mixed behavior.
- Refactor all affected files.
- Create new files if required.
- Delete obsolete code if no longer used.

---

# Validation Required

After coding:

1. Verify imports.
2. Verify syntax.
3. Verify command line arguments.
4. Verify CSV output generation.
5. Verify no write action exists inside check_lvd_status.py.
6. Verify toggle_lvd_checkbox.py only modifies configuration when argument == "check".

Do not stop after planning.

Implement the changes directly in the codebase.

At the end provide:

- Modified files
- Created files
- Deleted files
- Summary of changes