from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q
from django.utils.text import slugify

from apps.plans.models import Plan
from apps.products.models import Product
from apps.blog.models import BlogPost
from apps.jobs.models import Job


@api_view(['GET'])
@permission_classes([AllowAny])
def global_search(request):

    key = request.GET.get("key", "").strip()

    if not key:
        return Response({
            "status": False,
            "message": "Search key required",
            "data": []
        })

    results = []


    # ========================
    # PLANS SEARCH
    # ========================

    plans = Plan.objects.filter(
        Q(name__icontains=key) |
        Q(description__icontains=key) |
        Q(category__name__icontains=key)
    ).select_related("category")[:10]


    for plan in plans:

        results.append({

            "type": "plan",

            "title": plan.name,

            "slug": plan.slug,

            "category": plan.category.name if plan.category else None,

            "category_slug": plan.category.slug if plan.category else None,

        })


    # ========================
    # PRODUCTS SEARCH
    # ========================

    products = Product.objects.filter(
        Q(name__icontains=key) |
        Q(description__icontains=key) |
        Q(category__name__icontains=key)
    ).select_related("category")[:10]


    for product in products:

        results.append({

            "type": "product",

            "title": product.name,

            "slug": product.slug,

            "category": product.category.name if product.category else None,

            "category_slug": product.category.slug if product.category else None,

        })


    # ========================
    # BLOG SEARCH
    # ========================

    blogs = BlogPost.objects.filter(
        Q(title__icontains=key) |
        Q(content__icontains=key)
    )[:10]


    for blog in blogs:

        results.append({

            "type": "blog",

            "title": blog.title,

            "slug": blog.slug,

            "category": None,

            "category_slug": None,

        })


    # ========================
    # JOB SEARCH
    # ========================

    jobs = Job.objects.filter(
        Q(title__icontains=key) |
        Q(description__icontains=key) |
        Q(location__icontains=key)
    )[:10]


    for job in jobs:

        results.append({

            "type": "job",

            "title": job.title,

            # generate slug dynamically
            "slug": slugify(job.title),

            "category": None,

            "category_slug": None,

        })


    return Response({

        "status": True,

        "count": len(results),

        "data": results

    })