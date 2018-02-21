#!/usr/bin/env python
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, NoSuchWindowException
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

def login(user, passwd, wait=2):
    driver = webdriver.Chrome(Credential['path'])
    driver.maximize_window()
    driver.get("http://ticket.melon.com/main/index.htm")

    _ = WebDriverWait(driver, wait).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "li#name_area"))
    )
    print('loginstart')
    driver.execute_script("loginStrat()");

    _ = WebDriverWait(driver, wait).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input#id"))
    )
    userid = driver.find_element_by_id('id')
    userid.send_keys(user)

    password = driver.find_element_by_id('pwd')
    password.send_keys(passwd)

    button = driver.find_element_by_id('btnLogin')
    button.click()

    _ = WebDriverWait(driver, wait).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "a#btnLogout"))
    )
    return driver

def book(driver, wait=10):
    driver.execute_script("window.location.href = 'http://ticket.melon.com/performance/index.htm?prodId=201473'")
    print("location changed")

    _ = WebDriverWait(driver, wait).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "button.button.btColorGreen"))
    )

    driver.execute_script(simulate_click, driver.find_elements_by_css_selector('li.item_date.first')[0])
    driver.execute_script(simulate_click, driver.find_elements_by_css_selector('li.item_time')[1])
    driver.execute_script(simulate_click, driver.find_elements_by_css_selector('button.button.btColorGreen')[0])
#    driver.execute_script("document.oneForm.action = 'https://ticket.melon.com/reservation/popup/onestop.htm'; document.oneForm.target=''; document.oneForm.prodId.value = 201323; document.oneForm.pocCode.value='SC0002'; document.oneForm.scheduleNo.value=100001; document.oneForm.sellTypeCode.value='ST0001'; document.oneForm.tYn.value='Y'; document.oneForm.chk.value=encodeURIComponent(sessionKey); document.oneForm.netfunnel_key.value=':key=91E7B7437A0A6BDC88165C6699E69D015E9771A3C9B3FDABA73958FD409871F357DA86B3C40D2427CAD3661CA489CBCE93707968F538F191F9A4D7A8217D18F9FA538DA057289C4BE49E725524226633233C1DA9524C86E1BA645DCF257E26639C8193E3044FDD29871DD04FFF86553D74696F6E2C302C332C312C30&'; document.oneForm.submit();")

    _ = WebDriverWait(driver, wait).until(found_window("onstopForm"))

    _ = WebDriverWait(driver, wait).until(
            EC.frame_to_be_available_and_switch_to_it('oneStopFrame')
        )

    _ = WebDriverWait(driver, wait).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#divGradeSummary > tr:nth-child(2) > td > div > ul > li:nth-child(1)"))
        )

#    driver.execute_script("selectedBlock(this,'43','Floor,A','Floor','층','A','구역','SE0001')");
#    driver.execute_script("selectedBlock(this,'331','Floor,스탠딩 가','Floor','층','스탠딩 가','구역','SE0001')");
#    driver.execute_script("selectedBlock(this,'331','Floor,스탠딩 다','Floor','층','스탠딩 다','구역','SE0001')");
    driver.execute_script("selectedBlock(this,'36','1,C','1','층','C','열','SE0001')");

    trying = 0;
    while find_and_select_seats(driver, 0, wait):
        trying += 1
        print("keep finding and selecting seats", trying)

    return (driver, False)

def reload_schedule(driver, wait=0.1):
    print("reload_schedule every ", wait, " seconds")
    try:
        _ = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "btnReloadSchedule"))
        )
    except:
        print("btnReloadSchedule not found so it will stop reloading, please start the script again")
        return False

    driver.execute_script(simulate_click, driver.find_element_by_id("btnReloadSchedule"))
    return True

def check_alert_present(driver):
    try:
        _ = WebDriverWait(driver, 5).until(
                EC.alert_is_present())

        alert = driver.switch_to_alert()
        print(alert.text)

        alert.accept()
        return True
    except TimeoutException:
        print("no alert")
        return False

def find_and_select_seats(driver, count, wait):
    while (count == 0):
        try:
            _ = WebDriverWait(driver, wait).until(
                EC.invisibility_of_element_located((By.CSS_SELECTOR, "div#loadingLayer"))
            )
        except:
            print("loading layer was not dismissed in 10 seconds so it will be refreshed now")
            if not reload_schedule(driver):
                return True

        try:
            _ = WebDriverWait(driver, wait).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "rect[fill^='#d']"))
            )
        except:
            print("any rect element not found so it will be refreshed now")
            if not reload_schedule(driver):
                return True

        available_seats = driver.find_elements_by_css_selector("div#ez_canvas rect[fill^='#b']")
        print(available_seats)

        for seat in available_seats:
            if count == 0:
                print("seats are available!")
                driver.execute_script(simulate_click, seat);
                count = count + 1
                break

        if count == 1:
            print('seats exist')

            driver.execute_script(simulate_click, driver.find_element_by_id('nextTicketSelection'));

            while check_alert_present(driver):
                continue

            try:
                _ = WebDriverWait(driver, wait).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a#nextPayment"))
                    )
            except:
                print("No nextPayment element here")
                count = 0
                if not reload_schedule(driver):
                    return True

            driver.execute_script("arguments[0].selectedIndex = arguments[0].length - 1;", driver.find_elements_by_css_selector("dd.price.wrap_sel > select"))
            driver.execute_script(simulate_click, driver.find_element_by_id('nextPayment'));

            _ = WebDriverWait(driver, wait).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "a#btnFinalPayment"))
            )

            # fill out info
            tel2 = Credential['tel2']
            tel3 = Credential['tel3']
            driver.find_element_by_id('tel1').send_keys('010')
            driver.find_element_by_id('tel2').send_keys(tel2)
            driver.find_element_by_id('tel3').send_keys(tel3)

            driver.execute_script(simulate_click, driver.find_element_by_id('payMethodName003'));
            driver.execute_script("var elem = document.getElementsByName('bankCode')[0]; elem.selectedIndex = 7; elem.onchange();");
            driver.find_element_by_id('cashReceiptRegTelNo2').send_keys(tel2)
            driver.find_element_by_id('cashReceiptRegTelNo3').send_keys(tel3)
            driver.execute_script(simulate_click, driver.find_element_by_id('chkAgreeAll'));
            driver.execute_script(simulate_click, driver.find_element_by_id('btnFinalPayment'));
            raw_input("Press Enter to continue...")
        else:
            if not reload_schedule(driver):
                return True

    return False

def main(action=Login):
    user = Credential['user']
    pw = Credential['pw']

    driver = login(user, pw)
    ret = book(driver)

    ret[0].close()

if __name__ == '__main__':
    action = Login
    main(action=action)
