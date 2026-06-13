test_cases=[
    {"id":"TC_01", "title":"Valid login", "type":"positive"},
    {"id":"TC_02", "title":"Invalid login", "type":"negative"},
    {"id":"TC_03", "title":"Empty login", "type":"edgecases"}
]

print(test_cases[0]["id"])
titles=[]

for tc in test_cases:
    titles.append(tc["title"])
print(titles)


ids=[tc["id"] for tc in test_cases]
print(ids)

types=[tc["type"] for tc in test_cases]
print(types)




titles2=[]

for tc in test_cases:
   titles2.append( tc["title"])

print(titles2)

title3=[tc["title"] for tc in test_cases]
print(title3)