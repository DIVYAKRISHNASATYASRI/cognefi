import jwt
import time

# Paste your token from Swagger here
token = "eyJhbGciOiJSUzI1NiIsImNhdCI6ImNsX0I3ZDRQRDExMUFBQSIsImtpZCI6Imluc18zOUNSR3RaR2s3Z0xnSFUwOU1oRVJVSnFkZ3UiLCJ0eXAiOiJKV1QifQ.eyJleHAiOjE3NzAyMDM5MjcsImZ2YSI6Wzk5OTk5LC0xXSwiaWF0IjoxNzcwMjAwMzI3LCJpc3MiOiJodHRwczovL2ludGVybmFsLW1vbml0b3ItODMuY2xlcmsuYWNjb3VudHMuZGV2IiwibmJmIjoxNzcwMjAwMzE3LCJzaWQiOiJzZXNzXzM5Q1cyYTlRQVdmTUdFQWUxdThZNEFqRWRZWiIsInN0cyI6ImFjdGl2ZSIsInN1YiI6InVzZXJfMzlDUk1HSnhmZXBWdVFIYkJFT2tpR3ZQb1BoIiwidiI6Mn0.puO04J3u3HOYF4svP9ZvQzjATa0SWaZ3VvJeoSW5WdOxCWtWIOkmWVsYlP4CXpoLg4Kuh6GQkeCChkzTyLK12G8498BdlfL0LIMF9pJtrzXMMyjZhe15y4MdH6JaTs76AIRAl9ayxG9tbP1strKBwVvMPQ8CAxL2DONFQycz_FLqcj3ZxM-t5MCHTz8L8XKZlnogZuwqfjjMBwKS50gYJOLYlmyMSa6t_MwMu2Fe84iViV4XlPmokR6cWqwXb8MCNpGIzwSLHum08Dww5yG1aK8glZPy6QpiVQWqjlApgc0ZCLz4IkrSdLaw3fnbD9465u5jyFqKKHPLbIgmP6xLSg"

payload = jwt.decode(token, options={"verify_signature": False})
iat = payload.get('iat')
now = int(time.time())

print(f"Token Issued At (iat): {iat}")
print(f"Current System Time:   {now}")
print(f"Difference:            {iat - now} seconds")

if iat > now:
    print("❌ Your computer clock is BEHIND Clerk's server. Please sync your Windows/Mac clock.")
else:
    print("✅ Time is okay.")