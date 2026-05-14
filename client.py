import requests

url = "http://127.0.0.1:5000/rate"

data = {
    "user_id": 1,
    "book_id": 1,
    "rating": 4.5
}

response = requests.post(url, json=data)

print("Status:", response.status_code)
print("Odgovor:", response.json())