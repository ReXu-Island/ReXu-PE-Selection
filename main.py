import time
from rich.console import Console
from rich.table import Table
from getpass import getpass
from selenium import webdriver
from optparse import OptionParser
from timeit import default_timer as timer
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

selection_list = {
    1: "Basketball 1 篮球1班",
    2: "Basketball 3 篮球3班",
    3: "Golf 1 高尔夫1班",
    4: "Golf 2 高尔夫2班",
    5: "Fencing 击剑",
    6: "Football 1 足球1班",
    7: "Football 2 足球2班",
    8: "Table Tennis 1 乒乓球1班",
    9: "Tennis 1 网球1班",
    10: "Tennis2 网球2班",
    11: "Badminton 羽毛球",
    12: "Body Building 1 健身塑型1班",
    13: "Yoga 2 瑜伽2班",
    14: "Yoga 3 瑜伽3班",
    15: "Roller skating 轮滑",
    16: "Taekwondo 跆拳道",
    17: "Women's Self-defense 女子防身术",
    18: "Cheerleading 啦啦操",
    19: "Volleyball 排球",
    20: "Archery 射箭",
    21: "Chacha 2 恰恰2班",
    22: "Rumba 伦巴",
    23: "Exemption 申请免修"
}


def gen_asterisk_char(password):
    result = ""
    for i in range(len(password)):
        result += "*"
    return result


def init_optparser():
    parser = OptionParser()
    parser.add_option("-u", "--username", dest="username", help="Xjtlu username")
    parser.add_option("-p", "--password", dest="password", help="Xjtlu password")
    parser.add_option("-c", "--course", dest="course", help="PE course")
    (options, args) = parser.parse_args()
    return (options, args)


def get_username(options):
    if options.username != None:
        console.print("[+] Reading username from command line arguments directly...", style="purple")
        return options.username
    else:
        console.print("[*] Please Input Username: ", style="green", end="")
        username = input()
        return username


def get_password(options):
    if options.password != None:
        console.print("[+] Reading password from command line arguments directly...", style="purple")
        return options.password
    else:
        console.print("[*] Please Input Password: ", style="green", end="")
        password = getpass("")
        return password


def print_input(username, password, course_id):
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Key", style="blue", width=12)
    table.add_column("Value", style="green")
    table.add_row("Username", username)
    table.add_row("Password", gen_asterisk_char(password))
    table.add_row("Course", selection_list.get(course_id))
    console.print(table)

def do_login(username, password):
    console.print("[*] Inputing username: %s" % username, style="blue")
    username_input = WebDriverWait(driver, 10, 0.25).until(EC.visibility_of_element_located((By.ID, "username")))
    username_input.send_keys(username)
    console.print("[*] Inputing password: %s" % gen_asterisk_char(password), style="blue")
    password_input = driver.find_element_by_id("password")
    password_input.send_keys(password)
    console.print("[*] Try to login...", style="blue")
    login_btn = driver.find_element_by_id("loginbtn")
    login_btn.click()


def check_login_status():
    try:
        error_msg = driver.find_element_by_id("loginerrormessage")
        console.print("[-] Login failed: %s" % error_msg.get_attribute("text"), style="red")
        console.print("[*] Retrying...", style="blue")
        return False
    except:
        console.print("[+] Login successfully!", style="purple")
        return True


def get_course_selection():
    if options.course != None:
        console.print("[+] Reading course from command line arguments directly...", style="purple")
        return int(options.course)
    else:
        console.print("[*] Please choose your favourite course:", style="purple")
        success = False
        selection = 0
        for k, v in selection_list.items():
            console.print("%s.%s" % (k, v), style="orange4")
        while not success:
            try:
                selection = int(input(""))
                if selection < 1 or selection > 23:
                    console.print("[-] Invalid course selected, please try again", style="red")
                    console.print("[*] Please choose your favourite course:", style="purple", end="")
                    continue
                else:
                    success = True
                    break
            except:
                console.print("[-] Invalid course selected, please try again", style="red")
                console.print("[*] Please choose your favourite course:", style="purple", end="")
                continue
        return selection


def find_course_link():
    console.print("[*] Making course label visible...", style="blue")
    parent_course_label = WebDriverWait(driver, 20, 0.25).until(EC.visibility_of_element_located((By.ID, "label_2_13")))
    parent_course_label.click()
    console.print("[*] Reading course id...", style="blue")
    course_label = driver.find_element_by_xpath("//a[starts-with(@href,'https://peselection.xjtlu.edu.cn/course/view.php?id=')]")
    course_link = course_label.get_attribute("href")
    console.print("[*] Read course link from id completed...", style="blue")
    console.print("[*] Redirect url: %s" % course_link, style="purple")
    return course_link


def redirect_to_course_link(course_link):
    console.print("[*] Redirecting now...", style="blue")
    driver.get(course_link)


def check_if_selection_open(course_link):
    console.print("[*] Checking whether course selection has become available...", style="blue")
    driver.get(course_link)
    try:
        available_indicator = driver.find_element_by_xpath("//div[@class='box generalbox alert']")
        console.print("[-] %s" % available_indicator.text, style="red")
        console.print("[-] Sleep 800ms for refreshing...", style="blue")
        return False
    except:
        console.print("[+] Course selection is now available!", style="red")
        return True


def find_click_course(course_id):
    console.print("[+] Click %s now..." % selection_list.get(course_id), style="purple")
    course = driver.find_element_by_id("choice_" + str(course_id))
    course.click()


def submit_selection(course_id):
    console.print("[*] Ready to submit selection: %s" % selection_list.get(course_id), style="blue")
    submit_button = driver.find_element_by_css_selector(".button[value='Save my choice']")
    submit_button.click()
    console.print("[+] Submitted selection: %s!" % selection_list.get(course_id), style="red")


def confirm_selection():
    try:
        driver.find_element_by_class_name("responseheader")
        console.print("[+] Confirm course selection succeed", style="purple")
    except:
        console.print("[-] Confirm course selection failed", style="red")


def print_run_time():
    end_timer = timer()
    console.print("[+] Time elapsed: %.2fs" % int(end_timer - start_timer), style="gold1")


if __name__ == "__main__":
    console = Console()
    driver = webdriver.Firefox()
    console.print("[*] Easy PE Selection for Xjtlu started", style="green")
    console.print("[*] Version: 0.0.1 Beta Access", style="green")
    console.print("[*] Copyright (c) 2018-2022 Henry Wu <henrywu0103@protonmail.com>", style="green")
    start_timer = timer()
    (options, args) = init_optparser()
    username = get_username(options)
    password = get_password(options)
    course_id = get_course_selection()
    print_input(username, password, course_id)
    console.print("[*] Accessing PE Selection Web Page now...", style="blue")
    driver.get("https://peselection.xjtlu.edu.cn/")
    console.print("[*] Ready for authentication...", style="blue")
    driver.get("https://peselection.xjtlu.edu.cn/login/index.php")
    do_login(username, password)
    login_succeed = False
    while not login_succeed:
        login_succeed = check_login_status()
        if login_succeed:
            break
        else:
            do_login(username, password)
            continue
    course_link = find_course_link()
    redirect_to_course_link(course_link)
    selection_open = False
    while not selection_open:
        selection_open = check_if_selection_open(course_link)
        if selection_open:
            find_click_course(course_id)
            submit_selection(course_id)
            confirm_selection()
            print_run_time()
            break
        else:
            time.sleep(0.8)
            continue