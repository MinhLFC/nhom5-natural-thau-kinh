import os
import sys
import time
import http.server
import socketserver
import threading
from functools import partial
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, 'doc_images')
    os.makedirs(img_dir, exist_ok=True)

    # Start local HTTP server to capture exact local code changes
    port = 8765
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=base_dir)
    httpd = socketserver.TCPServer(('127.0.0.1', port), handler)
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()

    opt = Options()
    opt.add_argument('--headless=new')
    opt.add_argument('--window-size=1280,880')
    opt.add_argument('--force-device-scale-factor=1.5')

    driver = webdriver.Edge(options=opt)
    try:
        target_url = f'http://127.0.0.1:{port}/index.html'
        driver.get(target_url)
        time.sleep(2)

        # Helper to click by selector
        def click(sel):
            el = driver.find_element(By.CSS_SELECTOR, sel)
            driver.execute_script("arguments[0].click();", el)
            time.sleep(0.3)

        def set_input(sel, val):
            driver.execute_script(f"""
                var el = document.querySelector('{sel}');
                if (el) {{
                    el.value = {val};
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                }}
            """)
            time.sleep(0.3)

        def save_elem_shot(sel, fname):
            path = os.path.join(img_dir, fname)
            el = driver.find_element(By.CSS_SELECTOR, sel)
            el.screenshot(path)
            print(f"Saved: {fname}")

        def save_full_shot(fname):
            path = os.path.join(img_dir, fname)
            driver.save_screenshot(path)
            print(f"Saved full: {fname}")

        # ---------------- THÍ NGHIỆM 1 ----------------
        driver.execute_script("document.querySelector(\"a[href='#tn1']\").click();")
        time.sleep(1)

        # TN1 Overview
        save_full_shot("01_tn1_overview.png")
        save_elem_shot("#tn1 .lab-panel", "02_tn1_controls.png")

        # TKHT: Ray O only
        driver.execute_script("""
            var btnHt = document.querySelector('[data-group="r-type"] [data-val="ht"]');
            if (btnHt) btnHt.click();
            document.getElementById('r-ray-o').checked = true;
            document.getElementById('r-ray-o').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-p').checked = false;
            document.getElementById('r-ray-p').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-f').checked = false;
            document.getElementById('r-ray-f').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        save_elem_shot("#tn1 .lab-stage", "03_tn1_ht_ray_o.png")

        # TKHT: Ray P only
        driver.execute_script("""
            document.getElementById('r-ray-o').checked = false;
            document.getElementById('r-ray-o').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-p').checked = true;
            document.getElementById('r-ray-p').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-f').checked = false;
            document.getElementById('r-ray-f').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        save_elem_shot("#tn1 .lab-stage", "04_tn1_ht_ray_p.png")

        # TKHT: Ray F only
        driver.execute_script("""
            document.getElementById('r-ray-o').checked = false;
            document.getElementById('r-ray-o').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-p').checked = false;
            document.getElementById('r-ray-p').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-f').checked = true;
            document.getElementById('r-ray-f').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        save_elem_shot("#tn1 .lab-stage", "05_tn1_ht_ray_f.png")

        # TKHT: All 3 rays
        driver.execute_script("""
            document.getElementById('r-ray-o').checked = true;
            document.getElementById('r-ray-o').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-p').checked = true;
            document.getElementById('r-ray-p').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-f').checked = true;
            document.getElementById('r-ray-f').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        save_elem_shot("#tn1 .lab-stage", "06_tn1_ht_all_rays.png")

        # TKPK: Switch to PK
        driver.execute_script("""
            var btnPk = document.querySelector('[data-group="r-type"] [data-val="pk"]');
            if (btnPk) btnPk.click();
            document.getElementById('r-ray-o').checked = true;
            document.getElementById('r-ray-o').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-p').checked = false;
            document.getElementById('r-ray-p').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-f').checked = false;
            document.getElementById('r-ray-f').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        save_elem_shot("#tn1 .lab-stage", "07_tn1_pk_ray_o.png")

        # TKPK: Ray P only
        driver.execute_script("""
            document.getElementById('r-ray-o').checked = false;
            document.getElementById('r-ray-o').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-p').checked = true;
            document.getElementById('r-ray-p').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-f').checked = false;
            document.getElementById('r-ray-f').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        save_elem_shot("#tn1 .lab-stage", "08_tn1_pk_ray_p.png")

        # TKPK: Ray F only
        driver.execute_script("""
            document.getElementById('r-ray-o').checked = false;
            document.getElementById('r-ray-o').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-p').checked = false;
            document.getElementById('r-ray-p').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-f').checked = true;
            document.getElementById('r-ray-f').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        save_elem_shot("#tn1 .lab-stage", "09_tn1_pk_ray_f.png")

        # TKPK: All 3 rays
        driver.execute_script("""
            document.getElementById('r-ray-o').checked = true;
            document.getElementById('r-ray-o').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-p').checked = true;
            document.getElementById('r-ray-p').dispatchEvent(new Event('change'));
            document.getElementById('r-ray-f').checked = true;
            document.getElementById('r-ray-f').dispatchEvent(new Event('change'));
        """)
        time.sleep(0.5)
        save_elem_shot("#tn1 .lab-stage", "10_tn1_pk_all_rays.png")

        # ---------------- THÍ NGHIỆM 2 ----------------
        driver.execute_script("document.querySelector(\"a[href='#tn2']\").click();")
        time.sleep(1)

        # TN2 Overview
        save_full_shot("11_tn2_overview.png")
        save_elem_shot("#tn2 .lab-panel", "12_tn2_controls.png")

        # TKHT Case 1: d > 2f (f=10, d=25)
        driver.execute_script("""
            var btnHt = document.querySelector('[data-group="i-type"] [data-val="ht"]');
            if (btnHt) btnHt.click();
            var dIn = document.getElementById('i-d');
            var fIn = document.getElementById('i-f');
            if (fIn) { fIn.value = 10; fIn.dispatchEvent(new Event('input')); }
            var pBtn = document.querySelector('#i-presets button[data-k="2.5"]');
            if (pBtn) pBtn.click();
        """)
        time.sleep(0.5)
        save_elem_shot("#tn2 .lab-stage", "13_tn2_ht_case1_d_greater_2f.png")

        # TKHT Case 2: d = 2f (f=10, d=20)
        driver.execute_script("""
            var pBtn = document.querySelector('#i-presets button[data-k="2"]');
            if (pBtn) pBtn.click();
        """)
        time.sleep(0.5)
        save_elem_shot("#tn2 .lab-stage", "14_tn2_ht_case2_d_equal_2f.png")

        # TKHT Case 3: f < d < 2f (f=10, d=15)
        driver.execute_script("""
            var pBtn = document.querySelector('#i-presets button[data-k="1.5"]');
            if (pBtn) pBtn.click();
        """)
        time.sleep(0.5)
        save_elem_shot("#tn2 .lab-stage", "15_tn2_ht_case3_f_d_2f.png")

        # TKHT Case 4: d < f (f=10, d=5)
        driver.execute_script("""
            var pBtn = document.querySelector('#i-presets button[data-k="0.5"]');
            if (pBtn) pBtn.click();
        """)
        time.sleep(0.5)
        save_elem_shot("#tn2 .lab-stage", "16_tn2_ht_case4_d_less_f.png")

        # TKPK Case: d=20, f=10
        driver.execute_script("""
            var btnPk = document.querySelector('[data-group="i-type"] [data-val="pk"]');
            if (btnPk) btnPk.click();
            var pBtn = document.querySelector('#i-presets button[data-k="2"]');
            if (pBtn) pBtn.click();
        """)
        time.sleep(0.5)
        save_elem_shot("#tn2 .lab-stage", "17_tn2_pk_case.png")

        print("ALL_SCREENSHOTS_CAPTURED_SUCCESSFULLY")

    finally:
        driver.quit()
        try:
            httpd.shutdown()
        except Exception:
            pass

if __name__ == '__main__':
    main()
