#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoSuchWindowException, ElementNotVisibleException
import sys

from credential import Credential
from simulate import simulate_click

Login, Book = ("Login", "Book")

def found_window(name):
    def predicate(driver):
        try:
            driver.switch_to_window(name)
        except NoSuchWindowException:
            return False
        else:
            return True
    return predicate

def login(user, passwd, wait=10):
    options = webdriver.ChromeOptions();
    options.add_argument("--incognito");
    options.add_argument("--disable-popup-blocking");

    driver = webdriver.Chrome(executable_path=Credential['path'], chrome_options=options)
#    driver.maximize_window()
    driver.get("http://ticket.yes24.com/Pages/Perf/Detail/DetailSpecial.aspx?IdPerf=30728")

#    while EC.visibility_of_element_located((By.CSS_SELECTOR, "body > div.errorWrap")):
#        driver.implicitly_wait(30)
#        driver.get("http://ticket.yes24.com/Pages/Perf/Detail/DetailSpecial.aspx?IdPerf=30728")

    raw_input("Please login and go to the booking page popped up...")
    tryBooking(driver, wait)

def tryBooking(driver, wait):
    _ = WebDriverWait(driver, wait).until(found_window("INIpayStd_Return"))

    _ = WebDriverWait(driver, wait).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div#calendar.calendar")))

    driver.execute_script("fdc_CalDateClick(\"2018-08-29\")")
#    driver.execute_script(simulate_click, driver.find_elements_by_css_selector('a.dcursor')[0])
    _ = WebDriverWait(driver, wait).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "#ulTime > li")))
#    driver.execute_script('fdc_CalDateClick("2018-08-29")');
    driver.execute_script("fdc_ChoiceSeat();")

    raw_input("switch iframe...")

    try:
        _ = WebDriverWait(driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.NAME,'ifrmSeatFrame')))
    except:
        raw_input("try reloading page...")
        return reload_page(driver, wait)

    trying = 0;
    while find_and_select_seats(driver, 0, wait):
        trying += 1
        print("keep finding and selecting seats", trying)

    return (driver, False)

def find_and_select_seats(driver, count, wait):
    while (count == 0):
        try:
            _ = WebDriverWait(driver, wait).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class^='s'][id^='t'][title^='1']")))
        except:
            print("any desired seat not found so reload seats...")
            return reload_seats(driver, wait)

        available_seats = driver.find_elements_by_css_selector("div[class^='s'][id^='t'][title^='1']")
        print(available_seats)

        for seat in available_seats:
            if count == 0:
                print("seats are available!")
                driver.execute_script(simulate_click, seat)
                count = count + 1

        if count == 1:
            print('seats exist')
            driver.execute_script("ChoiceEnd()")

            if check_alert_present(driver):
                count = 0
                if not reload_seats(driver, wait):
                    return False
                continue

            _ = WebDriverWait(driver, wait).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div#StepCtrlBtn03")))

            driver.execute_script("fdc_PromotionEnd()")
            _ = WebDriverWait(driver, wait).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div#StepCtrlBtn04")))
            driver.execute_script("fdc_DeliveryEnd()")

            _ = WebDriverWait(driver, wait).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "input#rdoPays22")))

            driver.execute_script("fdc_PayMethodChange(document.getElementById('rdoPays22'))");
            driver.execute_script("arguments[0].selectedIndex = 4;", driver.find_elements_by_css_selector("select#selBank"))

            _ = WebDriverWait(driver, wait).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div#StepCtrlBtn05")))

            driver.execute_script(simulate_click, driver.find_element_by_id('cbxCancelFeeAgree'))
            driver.execute_script(simulate_click, driver.find_element_by_id('chkinfoAgree'))

            driver.execute_script("fdc_PrePayCheck()")

            while check_alert_present(driver):
                text = raw_input("input the captchaText")
                capcha = driver.find_element_by_id('captchaText')
                capcha.send_keys(text)
                driver.execute_script("fdc_PrePayCheck()")

        else:
            if not reload_seats(driver, wait):
                return False

def reload_page(driver, wait):
    driver.refresh()

    _ = WebDriverWait(driver, wait).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div#calendar.calendar")))

    driver.execute_script("fdc_CalDateClick(\"2018-08-29\")")
    driver.implicitly_wait(3)
    driver.execute_script("fdc_ChoiceSeat();")

    try:
        _ = WebDriverWait(driver, 10).until(
                EC.frame_to_be_available_and_switch_to_it((By.NAME,'ifrmSeatFrame')))
    except:
        raw_input("try reloading page...")
        return reload_page(driver, wait)

    return True

def reload_seats(driver, wait):
    try:
        _ = WebDriverWait(driver, wait).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div#dMapInfo")))
        driver.execute_script(simulate_click, driver.find_element_by_id("dMapInfo"))
        driver.implicitly_wait(1)
        driver.execute_script("ChangeBlock(0)")
        print("reload seats....")
        return True
    except:
        return reload_page(driver, wait)

def check_alert_present(driver):
    try:
        _ = WebDriverWait(driver, 5).until(
                EC.alert_is_present())
        alert = driver.switch_to_alert()
        alert.accept()
        return True
    except:
        return False

def main(action=Login):
    user = Credential['user']
    pw = Credential['pw']

    driver = login(user, pw)

if __name__ == '__main__':
    action = Login
    main(action=action)
