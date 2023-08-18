# map/views.py

import asyncio
from aiohttp import ClientSession
from django.shortcuts import render
from django.http import JsonResponse

from concurrent.futures import ThreadPoolExecutor

from .crawlKakaoMap import crawl_kakao, crawl_naver

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import json


@csrf_exempt
def crawl(request):
    if request.method == "POST":
        data = json.loads(request.body)
        store_name = data.get("store_name")

        # 스레드풀을 사용하여 크롤링 함수를 병렬 실행
        with ThreadPoolExecutor(max_workers=2) as executor:
            kakao_future = executor.submit(crawl_kakao, store_name)
            naver_future = executor.submit(crawl_naver, store_name)

            # 크롤링 함수 실행 결과를 가져옴
            kakao_results = kakao_future.result()
            naver_results = naver_future.result()

        return JsonResponse(
            {
                "kakao_results": kakao_results,
                "naver_results": naver_results,
            }
        )
    return JsonResponse({"message": "Invalid request method"})


def search_results(request):
    query = request.GET.get("q")
    # 실제 검색 결과를 얻는 작업을 수행하고, results 리스트에 결과를 추가합니다.
    # 여기서는 간단한 예시로 더미 데이터를 사용합니다.
    results = ["결과 1", "결과 2", "결과 3"]


#     context = {
#         "results": results,
#     }
#     return render(request, "search.html", context)
