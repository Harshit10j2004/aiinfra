import requests

print("write your requiremts for you application ")

print("REQ1: Type of application(backend, fullstack , frontend , ai model)")
req1 = input("REQ1: ")

print("REQ2: Focus on (cost-optimaztion , permormance , balanced")

req2 = input("REQ2: ")

print("REQ3: Want to go which provider")
req3 = input("REQ3: ")


promt = input("Your needs: ")

payload = {
    "application": req1,
    "focus": req2,
    "cloud": req3,
    "data": promt
}

response = requests.post(url="http://localhost:8000/testing", json=payload)

data = response.json()
print(data)
