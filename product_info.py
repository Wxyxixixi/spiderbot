from bs4 import BeautifulSoup
import datetime


def get_product_info(page, check_color = False):
    soup = BeautifulSoup(page, 'lxml')
    # 1.商品sku信息
    sku = soup.find('div', class_='product-intro__head-sku').text.strip('SKU:').strip()
    # 2.商品所属分类信息
    breadcrumps = []
    for div_node in soup.find_all('div', class_='bread-crumb__item'):
        breadcrump = div_node.text.strip()
        # print(breadcrump)
        breadcrumps.append(breadcrump)
    # 3. 商品简介、类型信息
    tags = []
    for div_node in soup.find_all('div', class_='product-intro__description-table-item'):
        tag = div_node.text.strip()
        # print(tag)
        tags.append(tag)
    # 4.商品名称
    name = soup.find('div', class_='product-intro__head-name').text.strip()
    # 5.商品review数量
    # check_reviews = soup.find('span', class_='product-intro__head-reviews-text color-blue-text')
    check_stars = soup.find('div', class_='product-intro__head-reviews')
    if check_stars != None:
        # print(check_stars)
        span_node = check_stars.find('span')
        # print(span_node)
        stars_and_review = span_node['aria-label']

        stars = stars_and_review.split(' ')[-3]
        reviews = stars_and_review.split(' ')[-2]
    else:
        stars = 'null'
        reviews = 'null'
    # 处理新商品没有reviews情况, 替换为new标签作为标识
    # if not check_reviews:
    #     reviews = check_reviews.text.strip()
    # else:
    #     reviews = soup.find('span', class_='new-label').text.strip()
    # 6. 商品价格、折扣信息
    price = soup.find('div', class_='product-intro__head-price j-expose__product-intro__head-price').text.strip()
    # 处理price标签下有无discount标签
    price_lst = price.split()
    if len(price_lst) == 3:
        have_discount = 'Yes'
        discount_price = price_lst[0]
        original_price = price_lst[1]
        discount = price_lst[2]
    elif len(price_lst) == 1:
        have_discount = 'No'
        original_price = price_lst[0]
        discount_price = 'Null'
        discount = 'Null'
    # 处理异常格式的price tag
    else:
        have_discount = 'Null'
        original_price = 'Null'
        discount_price = 'Null'
        discount = 'Null'
    # 7.商品size信息
    ## 商品size列表, 两种情况下的size爬取，label active ->有货, label disabled ->无货
    size_lst = ''
    for div_node in soup.find_all('div', class_='product-intro__size-choose'):
        for span_node in div_node.find_all('span', class_='inner'):
            size = span_node.text.strip()
            size_lst += size + ' '
            # print(size)
    # 8.商品Shein points
    find_shein_points = soup.find('span', class_='color-orange-tips')
    # 处理异常商品无shein标签情况
    if find_shein_points:
        shein_points = find_shein_points.text.strip()
    else:
        shein_points = 'Null'
    # 9. 商品hot标签 - hot标签位于颜色选择位置
    if check_color:
        check_hot = soup.find('div', class_='product-intro__color-radio product-intro__color-radio_active')
        check_hot_div = check_hot.find('div', class_='color-hot')
        if check_hot_div != None:
            hot_tag = 'HOT'
        else:
            hot_tag = '/'
    else:
        hot_tag = '/'

    # 10. Customers also viewed - 只记录推荐商品的sku
    recommend_product = []
    for section_node in soup.find_all('section', class_='S-product-item j-expose__product-item'):
        a_node = section_node.find('a')
        recomend_sku = a_node['data-sku']
        recommend_product.append(recomend_sku)

    # 11.记录信息读取时刻 - timestamp
    ct = datetime.datetime.now()

    print('product name:', name)
    print('sku:', sku)
    print('Hot:', hot_tag)
    print('average stars:', stars)
    print('reviews number:', reviews)
    print('商品标签：', tags)
    print('Category：', breadcrumps)
    print('Original price:', original_price)
    print('have discount:', have_discount)
    print('discount:', discount)
    print('discounted price:', discount_price)
    print('SHEIN points:', shein_points)
    print('Customers also viewed:', recommend_product)
    print('Sizes available:', size_lst)


    # 10. 商品数据写入csv
    data = {
        'sku': sku,
        'product name': name,
        'HOT tag': hot_tag,
        'average reviews': stars,
        'reviews': reviews,
        'Category': breadcrumps,
        'tags': tags,
        'Original price': original_price,
        'have discount': have_discount,
        'discount': discount,
        'discounted price': discount_price,
        'SHEIN points': shein_points,
        'Sizes available': size_lst,
        'Customers also viewed': recommend_product,
        'time stamp': ct
    }
    return data
