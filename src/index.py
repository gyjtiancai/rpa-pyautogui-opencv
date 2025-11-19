# 剪映RPA - 视觉方式实现RPA - 模板匹配算法
import pygetwindow as gw
import time
import pyautogui
import cv2
from pywinauto import Desktop
import os

# pywinauto查找并处理剪映窗口（废弃）
def find_and_handle_window():
    # 连接桌面并查找剪映窗口
    desktop = Desktop(backend="uia")  # 使用UIA后端，适合现代Windows应用
    # 查找剪映窗口
    capcut_window = desktop.window(title="剪映专业版")
    # 激活剪映窗口
    capcut_window.set_focus()
    # 等待剪映窗口激活
    time.sleep(1)

# 查找剪映窗口
def find_window(window_title):
    print(f'正在查找{window_title}窗口...')
    # 获取所有窗口标题
    titles = gw.getAllTitles()
    print(titles)
    # 获取所有窗口对象
    # windows = gw.getAllWindows()
    # print(windows)
    # 通过标题查找窗口（子字符串匹配，支持模糊匹配）
    jianying_windows = gw.getWindowsWithTitle(window_title)[0]
    print(jianying_windows)
    if(not jianying_windows):
        print(f'{window_title}窗口未找到')
        return None
    return jianying_windows

# 处理剪映窗口
def handle_window(jianying_windows):
    jianying_windows.activate()
    time.sleep(1)
    jianying_windows.maximize()
    time.sleep(1)

# 查找目标元素图像在屏幕图像中的位置
def find_element_position(element_img_path, screen_img_path, min_similarity=0.8):

    # 使用OpenCV读取按钮模板图片（需要查找的目标图片）
    # cv2.imread() 返回一个numpy数组，包含图片的像素数据（BGR格式）
    # 如果图片不存在或读取失败，将返回None
    btn_img = cv2.imread(element_img_path)

    # 使用OpenCV读取背景图片（包含按钮的完整屏幕截图）
    # 这是之前通过pyautogui.screenshot()保存的完整屏幕截图
    bg_img = cv2.imread(screen_img_path)

    # 使用模板匹配算法在背景图片中查找按钮图片的位置
    # cv2.matchTemplate() 会在bg_img中滑动btn_img，计算相似度
    # cv2.TM_CCOEFF_NORMED: 使用归一化相关系数匹配方法（值范围0-1，1表示完全匹配）
    # 返回一个结果矩阵，每个位置的值表示该位置的匹配度
    result = cv2.matchTemplate(bg_img, btn_img, cv2.TM_CCOEFF_NORMED)

    # 从匹配结果矩阵中提取最小值和最大值及其位置
    # min_val: 最小匹配值（相似度最低的位置）
    # max_val: 最大匹配值（相似度最高的位置，通常是我们要找的按钮位置）
    # min_loc: 最小值对应的坐标 (x, y)
    # max_loc: 最大值对应的坐标 (x, y) - 这就是按钮在背景图片中的左上角坐标
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 打印匹配结果信息，用于调试和验证
    # 通常max_val应该接近1.0（如0.8以上）表示匹配成功

    # max_loc[0]: 按钮左上角的x坐标
    # max_loc[1]: 按钮左上角的y坐标
    # btn_img.shape[1]: 按钮图片的宽度（列数）
    # btn_img.shape[0]: 按钮图片的高度（行数）
    # 通过加上宽度和高度的一半，计算出按钮的中心点坐标
    print(f'{element_img_path}最小匹配值（相似度最低的位置）', min_val)
    print(f'{element_img_path}最大匹配值（相似度最高的位置）', max_val)
    print(f'{element_img_path}最小相似度对应的坐标 (x, y)', min_loc)
    print(f'{element_img_path}最大相似度对应的坐标 (x, y)', max_loc)
    print(f'{element_img_path}图片的宽度（列数）', btn_img.shape[1])
    print(f'{element_img_path}图片的高度（行数）', btn_img.shape[0])
    x = max_loc[0] + btn_img.shape[1] / 2
    y = max_loc[1] + btn_img.shape[0] / 2
    print(f'{element_img_path}的中心点坐标 (x, y)', x, y)
    if(max_val < min_similarity):
        print(f'{element_img_path}匹配度低于0.8，目标元素未找到')
        return None, None
    return x, y

# 主函数
def main():
    # 查找剪映窗口
    jianying_windows = find_window('剪映专业版')
    if(not jianying_windows):
        return
    # 处理剪映窗口
    handle_window(jianying_windows)
    
    # 截图剪映窗口,保存至screenshots目录
    pyautogui.screenshot('screenshots/bg.png')

    # 查找"开始创作"元素图像在屏幕图像中的位置
    x, y = find_element_position('screenshots/btn_begin.png', 'screenshots/bg.png')
    # 如果存在“开始创作”按钮，说明在初始化界面，要先点击”开始创作“按钮，进入创作页面，并重新截创作背景图
    if(x and y):
        # 将鼠标移动到目标元素位置
        # duration=0.3: 鼠标移动动画持续0.3秒，使移动更自然
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(1)
        pyautogui.click()
        time.sleep(3)
        # 重新截图创作背景图
        pyautogui.screenshot('screenshots/bg.png')
    # 如果不存在“开始创作”按钮，则查找"导入"图像在屏幕图像中的位置
    x, y = find_element_position('screenshots/btn_import.png', 'screenshots/bg.png')
    if(x and y):
        # 将鼠标移动到目标元素位置
        # duration=0.3: 鼠标移动动画持续0.3秒，使移动更自然
        pyautogui.moveTo(x, y, duration=0.3)
        time.sleep(1)
        pyautogui.click()
        time.sleep(1)
    # TODO: 剪映操作
    # desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    # desktop_dir_path = os.path.join(desktop_path, 'sucai')
    # print('desktop_path',desktop_path, desktop_dir_path)
    # 遍历desktop_dir_path的所有视频
    # for file_name in os.listdir(desktop_dir_path):
    #     # 点击导入
    #     pyautogui.moveTo(350, 250, duration=0.3)
    #     time.sleep(1)
    #     pyautogui.click()
    #     time.sleep(1)
    #     print('file_name', file_name)
    #     # 移除file_name后缀
    #     file_name = file_name.split('.')[0]
    #     print('file_name', file_name)
    #     file_path = os.path.join(desktop_dir_path, file_name)
    #     print('file_path', file_path)
    #     pyautogui.write(file_path, interval=0.05)
    #     time.sleep(1)
    #     # 按下回车确认导入视频
    #     pyautogui.press('enter')
    #     time.sleep(1)
    #     pyautogui.press('enter')

    print('操作完成')

if __name__ == "__main__":
    main()