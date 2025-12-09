# 🔒 Rate Limiting & Security

## ✅ Already Implemented!

Rate limiting is **fully implemented** using `slowapi` in the backend.

---

## 📊 Current Rate Limits

### Per IP Address:

| Endpoint | Rate Limit | Purpose |
|----------|------------|---------|
| `/convert` | 20/minute | Code conversion |
| `/convert/stream` | 20/minute | Streaming conversion |
| `/analyze` | 20/minute | Code analysis |
| `/format` | 20/minute | Code formatting |
| `/explain` | 20/minute | Code explanation |
| `/execute` | 10/minute | Code execution (stricter) |
| `/batch-convert` | 5/minute | Batch operations (most strict) |

---

## 🛡️ How It Works

### 1. IP-Based Tracking
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

### 2. Decorator Application
```python
@app.post("/convert")
@limiter.limit("20/minute")
async def convert_code(request: Request, conv_request: ConversionRequest):
    # Conversion logic
```

### 3. Automatic Enforcement
- Tracks requests per IP address
- Returns `429 Too Many Requests` when exceeded
- Includes `Retry-After` header
- Resets every minute

---

## 🔐 Additional Security Layers

### Input Validation
```python
# Code length limits
if len(conv_request.code) > 100000:
    raise HTTPException(400, "Code too large. Max 100KB")

# Execution limits
if len(exec_request.code) > 10000:
    raise HTTPException(400, "Code too large for execution. Max 10KB")

# Batch limits
if len(batch_request.files) > 10:
    raise HTTPException(400, "Maximum 10 files per batch")
```

### Sandboxed Execution
```python
# 5-second timeout
result = subprocess.run(
    ['python3', temp_file],
    capture_output=True,
    text=True,
    timeout=5  # Prevents infinite loops
)
```

### Security Scanning
- SQL injection detection
- XSS vulnerability detection
- Hardcoded secrets detection
- Command injection detection
- Unsafe eval() detection

---

## 📈 Rate Limit Response

### When Limit Exceeded:
```json
{
  "error": "Rate limit exceeded: 20 per 1 minute",
  "detail": "Too Many Requests"
}
```

### Response Headers:
```
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1234567890
Retry-After: 60
```

---

## 🎯 Why These Limits?

### `/convert`, `/analyze`, `/format`, `/explain` - 20/minute
- **Reasoning**: Normal usage patterns
- **Allows**: ~1 request every 3 seconds
- **Protects**: Against rapid automated calls
- **Fair**: Enough for legitimate users

### `/execute` - 10/minute
- **Reasoning**: Resource-intensive operation
- **Allows**: ~1 execution every 6 seconds
- **Protects**: Server CPU/memory
- **Fair**: Sufficient for testing

### `/batch-convert` - 5/minute
- **Reasoning**: Most resource-intensive
- **Allows**: ~1 batch every 12 seconds
- **Protects**: Against bulk abuse
- **Fair**: Adequate for batch workflows

---

## 🔧 Configuration

### Current Settings (in `main.py`):
```python
# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

### To Adjust Limits:
```python
# Change decorator value
@limiter.limit("30/minute")  # Increase to 30
@limiter.limit("10/minute")  # Decrease to 10
@limiter.limit("100/hour")   # Use hourly limit
```

---

## 📊 Monitoring

### Logs Include:
```
INFO: Converting python to javascript
INFO: Conversion successful
WARNING: Rate limit exceeded for IP 192.168.1.1
```

### Metrics to Track:
- Total requests per endpoint
- Rate limit violations per IP
- Average response times
- Error rates

---

## 🚀 Production Deployment

### Fly.io (Current):
- ✅ Rate limiting active
- ✅ Auto-scaling enabled
- ✅ Health checks configured
- ✅ Logging enabled

### Docker:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🧪 Testing Rate Limits

### Test Script:
```bash
#!/bin/bash
# Test rate limiting

for i in {1..25}; do
  echo "Request $i:"
  curl -X POST https://ai-code-converter-manzi.fly.dev/convert \
    -H "Content-Type: application/json" \
    -d '{"source_language": "python", "target_language": "javascript", "code": "print(\"test\")"}' \
    -w "\nStatus: %{http_code}\n\n"
  sleep 2
done
```

### Expected Results:
- Requests 1-20: `200 OK`
- Requests 21+: `429 Too Many Requests`
- After 60 seconds: Resets to 0

---

## 💡 Best Practices

### For Users:
1. **Respect rate limits** - Don't spam requests
2. **Use batch endpoints** - For multiple files
3. **Cache results** - Don't re-convert same code
4. **Handle 429 errors** - Implement retry logic

### For Developers:
1. **Monitor logs** - Track abuse patterns
2. **Adjust limits** - Based on usage data
3. **Add caching** - Reduce duplicate requests
4. **Use CDN** - For static assets

---

## 🔄 Future Enhancements

### Planned:
- [ ] Redis-based rate limiting (distributed)
- [ ] User authentication & API keys
- [ ] Tiered rate limits (free vs paid)
- [ ] Rate limit dashboard
- [ ] IP whitelist/blacklist
- [ ] Geographic rate limiting

### Possible:
- [ ] Token bucket algorithm
- [ ] Sliding window rate limiting
- [ ] Per-user quotas
- [ ] Cost-based rate limiting

---

## 📚 Dependencies

### Required:
```txt
slowapi==0.1.9
```

### Already in `requirements.txt`:
```bash
cd backend
grep slowapi requirements.txt
# Output: slowapi==0.1.9
```

---

## ✅ Summary

**Rate limiting is FULLY IMPLEMENTED and ACTIVE!**

- ✅ Per-IP tracking
- ✅ Multiple rate limits per endpoint
- ✅ Automatic enforcement
- ✅ Proper error responses
- ✅ Production-ready
- ✅ Documented in README
- ✅ No additional setup needed

**Just deploy and it works!** 🚀

---

**Protection Status: ACTIVE ✅**
**Pay-as-you-go Protection: ENABLED ✅**
**Abuse Prevention: CONFIGURED ✅**
