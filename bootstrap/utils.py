def local_page_range(page, num=7):
    if num % 2 == 0:
        raise ValueError('Page count (%s) should be an odd number.' % num)
    if page.paginator.num_pages <= num:
        return [i+1 for i in range(page.paginator.num_pages)]
    n = num // 2
    start = page.number - n
    end = page.number + n
    while start <= 0:
        start += 1
        end += 1
    while end > page.paginator.num_pages:
        start -= 1
        end -= 1
    return list(range(start, end+1))
