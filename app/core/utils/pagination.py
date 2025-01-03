from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate_queryset(queryset, page_number, items_per_page=10):
    paginator = Paginator(queryset, items_per_page)
    try:
        page = paginator.page(page_number)
    except (EmptyPage, PageNotAnInteger):
        page = paginator.page(1)  # Default to the first page if the page number is invalid

    return page
