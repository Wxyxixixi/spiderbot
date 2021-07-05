from bs4 import BeautifulSoup
from selenium import webdriver
from urllib.parse import urljoin
from product_info import get_product_info
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
import time
import csv

## 创建空csv表格文档及表头
file = open('t_mul_pages.csv', 'w', newline='')
writer = csv.writer(file)
writer.writerow([
        'sku', 'product name', 'HOT', 'stars', 'reviews', 'Category', 'tags',
        'Original price', 'have discount', 'discount', 'discounted price',
        'SHEIN points', 'Sizes available', 'Customers also viewed(sku)', 'timestamp', '[no. page,item]'
    ])


# 配置chrome浏览器不加载图片
chrome_options = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_options.add_experimental_option("prefs",prefs)
chrome_options.add_argument('--headless')
driver = webdriver.Chrome(chrome_options=chrome_options)

# 设置隐式等待时间
wait = WebDriverWait(driver, 10, 0.5)

# URL 女装 - 裙装第一页 （ 下称'货架'）
url = 'https://www.shein.com/Dresses-c-1727.html'
driver.get(url)
# time.sleep(3)
# 隐式等待策略 - 以加速
wait.until(lambda diver: driver.find_element_by_css_selector('[class="svgicon svgicon-close"]'))
## 反反爬策略1 - 关闭优惠券 Step 3 - A window bumps up, click close - 关闭优惠券窗口
button = driver.find_element_by_css_selector('[class="svgicon svgicon-close"]')
if button:
    button.click()
# time.sleep(5)
soup_page = BeautifulSoup(driver.page_source, 'lxml')

# 读取总页数
max_pages = soup_page.find('span', class_="S-pagination__total").text.strip()
max_pages = int(max_pages)
# 读取货架页面商品数量


# 先记录每一页的soup信息，放进列表，再从列表中读取商品
soup_list = []
soup_list.append(soup_page)  # 放入第一页

for i in range(max_pages):
    driver.find_element_by_css_selector(
        '[class = "S-pagination__arrow S-pagination__arrow-next iconfont-s icons-Jump-Alert"]').click()  # 翻页
    time.sleep(3)
    soup_list.append(BeautifulSoup(driver.page_source, 'lxml'))

T1 = time.time()

# 开始爬取商品货架上各商品页面 Step 4 - Iterate over all the products by entering each
for page_i, page in enumerate(soup_list):
    count = 0
    # 当前页面商品总量 max_num
    section_node = soup_page.find_all('section',
                                      class_='S-product-item j-expose__product-item product-list__item')[-1]
    max_item = section_node['data-ada-pos']
    max_num = int(max_item) + 1

    for node_i, section_node in enumerate(page.find_all('section', class_='S-product-item j-expose__product-item product-list__item')):
        if count <= max_num:
            ## a_node contains the link to the product page, label by 'href' - 从货架进入商品页面
            div_node = section_node.find('div')
            a_node = div_node.find('a')
            href = a_node['href']
            url_detail = urljoin(url, href)  # url + href = link
            product_url = str(url_detail)
            driver.get(url_detail)  # driver enters into the product link 进入商品页面


            # 反反爬策略2：以防有banner挡住颜色按钮
            if driver.find_elements_by_css_selector('[class = "c-quick-register j-quick-register"]'):
                # 优惠券banner没有收起
                button = driver.find_element_by_css_selector('[class = "svgicon svgicon-arrow-left"]')
                if button:
                    # 点击收起优惠券banner
                    button.click()
            # 同一商品是否有颜色分类 - color 有时有两种标签
            colors1 = driver.find_elements_by_css_selector('[class = "product-intro__color-block"]')
            colors2 = driver.find_elements_by_css_selector('[class = "product-intro__color-radio"]')
            if colors1 or colors2:
                info = get_product_info(driver.page_source, check_color=True)  # main page infos
                writer.writerow(info.values())
                colors = colors1 if colors1 else colors2
                # print(colors)
                for color_button in colors:
                    # print(color_button)
                    # 点击另一颜色/款式
                    color_button.send_keys(Keys.ENTER)
                    time.sleep(1)
                    # 显示等待策略 - 须等浏览器加载完customers also viewed
                    wait.until(lambda diver: driver.find_element_by_css_selector('[class="S-product-item__img-container j-expose__product-item-img"]'))
                    info = get_product_info(driver.page_source, check_color=True)
                    # 记录当前商品位于本次抓取的页数和页面所在序列数
                    info['page, item'] = str(page_i) + str(node_i)
                    # 写入表格信息
                    writer.writerow(info.values())
            else:
                wait.until(lambda diver: driver.find_element_by_css_selector('[class="S-product-item__img-container j-expose__product-item-img"]'))
                info = get_product_info(driver.page_source)
                info['page, item'] = str(page_i) + str(node_i)
                # write the infos to the csv file
                writer.writerow(info.values())

            # driver.back()  # back to the last page to enter the next product page
            time.sleep(3)
            # print(count)
            count += 1


T2 = time.time()
# 打印程序运行时间
print('程序运行时间:%s秒' % (T2 - T1))
# driver.quit()
