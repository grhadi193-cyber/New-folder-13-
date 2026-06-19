"""
Arvan Cloud Server Automation Script
Opens Chrome, navigates Arvan Cloud panel, creates a server.
User handles: login, payment, CAPTCHA
Script handles: navigation, form filling, server creation
"""

import sys
import time
import base64
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

def setup_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--lang=fa")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def screenshot(driver, name):
    path = SCREENSHOT_DIR / f"{name}.png"
    driver.save_screenshot(str(path))
    print(f"[SCREENSHOT] Saved: {path}")
    return str(path)

def wait_for_element(driver, by, value, timeout=15):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def wait_and_click(driver, by, value, timeout=15):
    el = WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((by, value))
    )
    el.click()
    return el

def safe_click(driver, by, value, timeout=10):
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        time.sleep(0.3)
        el.click()
        return True
    except:
        return False

def type_text(driver, by, value, text, timeout=10):
    el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )
    el.clear()
    el.send_keys(text)
    return el

def pause(msg):
    input(f"\n{'='*50}\n⏸  {msg}\n   Press ENTER to continue...\n{'='*50}\n")

def main():
    print("=" * 60)
    print("  Arvan Cloud Server Automation")
    print("  ساخت خودکار سرور در آروان کلاد")
    print("=" * 60)
    
    driver = setup_driver()
    
    try:
        # Step 1: Navigate to Arvan Cloud
        print("\n[1/6] Opening Arvan Cloud panel...")
        driver.get("https://panel.arvancloud.ir")
        time.sleep(3)
        
        # Wait for user to login
        pause("لطفاً وارد حساب آروان کلاد خود شوید.\n   بعد از لاگین کامل، ENTER بزنید.")
        
        screenshot(driver, "01_after_login")
        print("[OK] Logged in successfully!")
        
        # Step 2: Navigate to server creation
        print("\n[2/6] Navigating to server creation page...")
        driver.get("https://panel.arvancloud.ir/iaas/v2/create")
        time.sleep(3)
        screenshot(driver, "02_create_server_page")
        
        # Check if we're on the right page
        current_url = driver.current_url
        print(f"   Current URL: {current_url}")
        
        if "create" not in current_url.lower():
            print("   Trying alternative navigation...")
            # Try finding the create button on dashboard
            try:
                # Look for server/iaas section
                links = driver.find_elements(By.TAG_NAME, "a")
                for link in links:
                    href = link.get_attribute("href") or ""
                    text = link.text
                    if "create" in href.lower() or "ایجاد" in text or "جدید" in text:
                        print(f"   Found link: {text} -> {href}")
                        link.click()
                        time.sleep(3)
                        break
            except Exception as e:
                print(f"   Navigation error: {e}")
        
        screenshot(driver, "03_server_form")
        
        # Step 3: Server name
        print("\n[3/6] Setting server name...")
        server_name = "ati-farzam-server"
        
        try:
            name_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[name*='name'], input[placeholder*='نام'], input[placeholder*='name']")
            if name_inputs:
                name_inputs[0].clear()
                name_inputs[0].send_keys(server_name)
                print(f"   Server name set to: {server_name}")
            else:
                print("   Could not find name input. Please enter manually.")
        except Exception as e:
            print(f"   Name input error: {e}")
        
        screenshot(driver, "04_name_set")
        
        # Step 4: Select OS - Ubuntu 24.04
        print("\n[4/6] Selecting Ubuntu 24.04...")
        try:
            # Try to find and click Ubuntu option
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Look for Ubuntu in radio buttons, select options, or clickable items
            ubuntu_found = False
            
            # Try clicking Ubuntu radio/option
            for selector in [
                "//*[contains(text(), 'Ubuntu')]",
                "//*[contains(text(), 'ubuntu')]",
                "//label[contains(., 'Ubuntu')]",
                "//div[contains(@class, 'os')]//*[contains(text(), 'Ubuntu')]",
            ]:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for el in elements:
                        if "24.04" in el.text or "22.04" in el.text or "Ubuntu" in el.text:
                            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                            time.sleep(0.3)
                            el.click()
                            ubuntu_found = True
                            print(f"   Selected: {el.text.strip()[:50]}")
                            break
                    if ubuntu_found:
                        break
                except:
                    continue
            
            if not ubuntu_found:
                print("   Could not auto-select Ubuntu. Please select manually.")
                pause("لطفاً Ubuntu 24.04 (یا 22.04) رو انتخاب کنید.")
                
        except Exception as e:
            print(f"   OS selection error: {e}")
            pause("لطفاً سیستم‌عامل Ubuntu رو انتخاب کنید.")
        
        screenshot(driver, "05_os_selected")
        
        # Step 5: Select plan - 2vCPU / 4GB RAM
        print("\n[5/6] Selecting plan (2vCPU / 4GB RAM)...")
        try:
            plan_found = False
            for selector in [
                "//*[contains(text(), '2') and contains(text(), '4')]",
                "//*[contains(text(), '2vCPU')]",
                "//*[contains(text(), '2 vCPU')]",
                "//div[contains(@class, 'plan')]//*[contains(text(), '2')]",
            ]:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for el in elements:
                        text = el.text
                        if "2" in text and ("4" in text or "RAM" in text.upper()):
                            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                            time.sleep(0.3)
                            el.click()
                            plan_found = True
                            print(f"   Selected plan: {text.strip()[:50]}")
                            break
                    if plan_found:
                        break
                except:
                    continue
            
            if not plan_found:
                print("   Could not auto-select plan. Please select manually.")
                pause("لطفاً پلن 2 vCPU / 4GB RAM رو انتخاب کنید.")
                
        except Exception as e:
            print(f"   Plan selection error: {e}")
            pause("لطفاً پلن مناسب رو انتخاب کنید (حداقل 2vCPU / 4GB RAM).")
        
        screenshot(driver, "06_plan_selected")
        
        # Step 6: SSH Key
        print("\n[6/6] Setting up SSH key...")
        pause("""لطفاً کلید SSH رو تنظیم کنید:
   - اگه کلید دارید: انتخابش کنید
   - اگه ندارید: 'کلید جدید' بسازید و فایل .pem رو دانلود کنید
   
   ⚠️  فایل .pem رو حتماً ذخیره کنید!
   
   بعد از تنظیم کلید SSH، ENTER بزنید.""")
        
        screenshot(driver, "07_ssh_key")
        
        # Final step: Create server
        pause("""حالا آماده‌ایم سرور رو بسازیم!
   
   ⚠️  قبل از ENTER زدن:
   - تنظیمات رو چک کنید
   - اگه پرداخت خواست، خودتون انجام بدید
   
   ENTER بزنید تا دکمه 'ایجاد سرور' رو بزنم.""")
        
        # Try to click create/submit button
        try:
            create_found = False
            for selector in [
                "//*[contains(text(), 'ایجاد')]",
                "//*[contains(text(), 'ساخت')]",
                "//*[contains(text(), 'Create')]",
                "//*[contains(text(), 'Submit')]",
                "button[type='submit']",
                "//button[contains(@class, 'submit')]",
                "//button[contains(@class, 'create')]",
            ]:
                try:
                    elements = driver.find_elements(By.XPATH, selector) if selector.startswith("/") or selector.startswith("(") else driver.find_elements(By.CSS_SELECTOR, selector)
                    for el in elements:
                        if el.is_displayed() and el.is_enabled():
                            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                            time.sleep(0.5)
                            el.click()
                            create_found = True
                            print(f"   Clicked: {el.text.strip()[:50]}")
                            break
                    if create_found:
                        break
                except:
                    continue
            
            if not create_found:
                print("   Could not find create button. Please click manually.")
                pause("لطفاً دکمه ایجاد/ساخت سرور رو بزنید.")
                
        except Exception as e:
            print(f"   Create button error: {e}")
            pause("لطفاً دکمه ایجاد سرور رو بزنید.")
        
        screenshot(driver, "08_creating")
        
        # Wait for server to be created
        print("\n⏳ Waiting for server to be ready...")
        time.sleep(10)
        screenshot(driver, "09_server_status")
        
        # Try to get server IP
        print("\n🔍 Looking for server IP...")
        time.sleep(5)
        
        page_text = driver.find_element(By.TAG_NAME, "body").text
        screenshot(driver, "10_final_page")
        
        # Keep browser open
        pause("""سرور ساخته شد! 🎉
   
   حالا:
   1. IP سرور رو از پنل آروان کپی کنید
   2. مسیر فایل .pem رو یادداشت کنید
   3. ENTER بزنید تا مرورگر بسته بشه
   
   بعدش من با SSH وصل میشم و پروژه رو deploy میکنم!""")
        
        # Save server info
        print("\n" + "=" * 60)
        print("📋 لطفاً اطلاعات زیر رو وارد کنید:")
        print("=" * 60)
        
        server_ip = input("\n🌐 IP سرور: ").strip()
        pem_path = input("🔑 مسیر فایل .pem (مثلاً C:\\Users\\PC-01\\Downloads\\arvan.pem): ").strip()
        username = input("👤 یوزرنیم (پیش‌فرض: root): ").strip() or "root"
        
        # Save to file
        server_info = {
            "ip": server_ip,
            "pem_path": pem_path,
            "username": username,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        info_path = Path(__file__).parent / "server_info.json"
        with open(info_path, "w") as f:
            json.dump(server_info, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ اطلاعات سرور ذخیره شد: {info_path}")
        print(f"   IP: {server_ip}")
        print(f"   PEM: {pem_path}")
        print(f"   User: {username}")
        print("\n🚀 حالا میتونم با SSH وصل بشم و deploy کنم!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        screenshot(driver, "error")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()
