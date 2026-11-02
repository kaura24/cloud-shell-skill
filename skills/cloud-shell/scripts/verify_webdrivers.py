#!/usr/bin/env python3
"""Verify Chromium/chromedriver and Firefox/geckodriver with local pages."""

import argparse
import sys


def check_browser(name, binary):
    from selenium import webdriver

    driver = None
    try:
        if name == "chromium":
            options = webdriver.ChromeOptions()
            options.binary_location = binary
            options.add_argument("--headless=new")
            driver = webdriver.Chrome(options=options)
        else:
            options = webdriver.FirefoxOptions()
            if binary:
                options.binary_location = binary
            options.add_argument("-headless")
            driver = webdriver.Firefox(options=options)

        driver.get("data:text/html,<title>CloudShellDriverCheck</title>")
        if driver.title != "CloudShellDriverCheck":
            raise RuntimeError(f"unexpected title: {driver.title!r}")
        caps = driver.capabilities
        driver_version = caps.get("moz:geckodriverVersion")
        if name == "chromium":
            driver_version = caps.get("chrome", {}).get("chromedriverVersion")
        print(f"PASS {name}: browser={caps.get('browserVersion', 'unknown')} "
              f"driver={driver_version or 'not reported'}")
        return True
    except Exception as exc:
        print(f"FAIL {name}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return False
    finally:
        if driver is not None:
            driver.quit()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chromium", required=True, help="Path to Chromium executable")
    parser.add_argument("--firefox", help="Path to Firefox executable, if not discoverable")
    args = parser.parse_args()
    try:
        import selenium  # noqa: F401
    except ImportError:
        print("FAIL: Selenium is not installed in this Python environment", file=sys.stderr)
        return 1
    results = [check_browser("chromium", args.chromium),
               check_browser("firefox", args.firefox)]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
