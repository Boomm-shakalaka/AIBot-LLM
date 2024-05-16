# from langchain_community.tools import DuckDuckGoSearchResults
# import asyncio
# async def get_search_results(question):
#     search = DuckDuckGoSearchResults()
#     results=search.run(question)
#     return results

# async def duckduck_search(question):
#     ddgs_results = await get_search_results(question)
#     return ddgs_results


# from duckduckgo_search import ddg  
# r = ddg("the latest cnn news", max_results=5)  
# for page in r:  
#     print(page)  
# question='the latest cnn news'
# search_result=asyncio.run(duckduck_search(question))
# print(search_result)
from duckduckgo_search import DDGS

# results = DDGS().text("德国时间", max_results=5)
# print(results)
results = DDGS().text("NBA比赛")
print(results)
