from django.utils import timezone


def filter_published_posts(queryset):
    return queryset.filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    )
