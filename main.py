import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, Response

app = FastAPI(title="Location & Monetag Service")

# 1. Настройка CORS для предотвращения блокировок браузером
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aniq Joylashuv va Eng Yaqin Maktab</title>

    <!-- Monetag Reklama Skripti -->
    <script src="https://quge5.com/88/tag.min.js" data-zone="284587" async data-cfasync="false"></script>

    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 35px;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 550px;
            transition: all 0.3s ease;
        }
        h2 {
            text-align: center;
            color: #2d3748;
            font-size: 24px;
            margin-bottom: 25px;
            border-bottom: 2px solid #edf2f7;
            padding-bottom: 15px;
        }
        .info {
            margin: 16px 0;
            font-size: 16px;
            color: #4a5568;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f7fafc;
            padding: 12px 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .info span {
            font-weight: 600;
            color: #2b6cb0;
            text-align: right;
            word-break: break-word;
            max-width: 60%;
        }
        .btn-location {
            width: 100%;
            background: #667eea;
            color: white;
            border: none;
            padding: 14px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 10px;
            cursor: pointer;
            margin-top: 15px;
            transition: background 0.3s ease;
        }
        .btn-location:hover {
            background: #5a67d8;
        }
        .ad-container {
            margin-top: 20px;
            width: 100%;
            max-width: 550px;
            text-align: center;
        }
        @media (max-width: 480px) {
            .card { padding: 20px; }
            .info { font-size: 14px; flex-direction: column; align-items: flex-start; }
            .info span { max-width: 100%; text-align: left; margin-top: 5px; }
        }
    </style>
</head>
<body>

<div class="card">
    <h2>📍 Joylashuv va Maktab Tizimi</h2>
    <div class="info">IP Manzil: <span id="ip">Yuklanmoqda...</span></div>
    <div class="info">Aniq Manzil: <span id="location">Ruxsat berilmagan</span></div>
    <div class="info">Eng Yaqin Maktab: <span id="school">Kutilmoqda...</span></div>
    <div class="info">Qurilma Nomi: <span id="device-model">Aniqlanmoqda...</span></div>
    <div class="info">Versiya: <span id="os-version">Aniqlanmoqda...</span></div>

    <button class="btn-location" onclick="requestLocation()">📍 Joylashuvni Aniqlash</button>
</div>

<div class="ad-container">
    <!-- Banner / Native Ads uchun joy -->
</div>

<script>
    async function getDeviceInfo() {
        const ua = navigator.userAgent;
        let model = "Noma'lum qurilma";
        let version = "Noma'lum versiya";

        if (navigator.userAgentData && navigator.userAgentData.getHighEntropyValues) {
            try {
                const hints = await navigator.userAgentData.getHighEntropyValues(["model", "platformVersion"]);
                if (hints.model) model = hints.model;
                if (hints.platformVersion) {
                    let majorVer = parseInt(hints.platformVersion.split('.')[0]);
                    version = majorVer >= 10 ? "Android " + majorVer : "Android " + hints.platformVersion;
                }
            } catch (e) {
                console.log("Client Hints error:", e);
            }
        }

        if (model === "Noma'lum qurilma") {
            if (/android/i.test(ua)) {
                let match = ua.match(/Android\s([0-9\.]+)/i);
                if (match) version = "Android " + match[1];
                let parts = ua.split(';');
                for (let part of parts) {
                    if (part.includes('Build/')) {
                        let subParts = part.trim().split(' ');
                        let buildIdx = subParts.findIndex(p => p.startsWith('Build/'));
                        if (buildIdx > 0) model = subParts[buildIdx - 1];
                    }
                }
            } else if (/iphone|ipad|ipod/i.test(ua)) {
                model = /ipad/i.test(ua) ? "Apple iPad" : "Apple iPhone";
                let verMatch = ua.match(/OS\s([0-9_]+)/i);
                if (verMatch) version = "iOS " + verMatch[1].replace(/_/g, '.');
            } else if (/windows/i.test(ua)) {
                model = "Windows PC";
                version = "Windows OS";
            } else if (/macintosh|mac os x/i.test(ua)) {
                model = "Macintosh";
                version = "Mac OS";
            }
        }

        document.getElementById('device-model').innerText = model;
        document.getElementById('os-version').innerText = version;
    }

    getDeviceInfo();

    function calculateDistance(lat1, lon1, lat2, lon2) {
        let R = 6371e3;
        let φ1 = lat1 * Math.PI/180;
        let φ2 = lat2 * Math.PI/180;
        let Δφ = (lat2-lat1) * Math.PI/180;
        let Δλ = (lon2-lon1) * Math.PI/180;

        let a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
                Math.cos(φ1) * Math.cos(φ2) *
                Math.sin(Δλ/2) * Math.sin(Δλ/2);
        let c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c;
    }

    async function loadIP() {
        try {
            let res = await fetch('/api/info');
            let data = await res.json();
            document.getElementById('ip').innerText = data.ip_manzili;
        } catch (e) {
            document.getElementById('ip').innerText = "Aniqlab bo'lmadi";
        }
    }

    function requestLocation() {
        document.getElementById('location').innerText = "Ruxsat so'ralmoqda...";
        document.getElementById('school').innerText = "Qidirilmoqda...";

        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(async (position) => {
                let lat = position.coords.latitude;
                let lon = position.coords.longitude;

                // 1. Nominatim Reverse Geocoding
                try {
                    let controller = new AbortController();
                    let timeoutId = setTimeout(() => controller.abort(), 5000);

                    let geoRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1&accept-language=uz`, {
                        signal: controller.signal,
                        headers: { 'User-Agent': 'FastAPI-Location-App/1.0' }
                    });
                    clearTimeout(timeoutId);
                    let geoData = await geoRes.json();
                    let addr = geoData.address || {};

                    let parts = [];
                    if (addr.state || addr.region) parts.push(addr.state || addr.region);
                    if (addr.city || addr.town || addr.county) parts.push(addr.city || addr.town || addr.county);
                    if (addr.suburb || addr.district) parts.push(addr.suburb || addr.district);
                    if (addr.road) parts.push(addr.road + " ko'chasi");

                    document.getElementById('location').innerText = parts.length > 0 ? parts.join(", ") : "Topildi";
                } catch (err) {
                    document.getElementById('location').innerText = "Manzilni aniqlab bo'lmadi";
                }

                // 2. Overpass API for Schools
                try {
                    let overpassUrl = `https://overpass-api.de/api/interpreter?data=[out:json];(node[amenity=school](around:4000,${lat},${lon});way[amenity=school](around:4000,${lat},${lon}););out center;`;
                    let schoolRes = await fetch(overpassUrl);
                    let schoolData = await schoolRes.json();
                    let elements = schoolData.elements;

                    if (elements && elements.length > 0) {
                        let nearest = null;
                        let minDistance = Infinity;

                        elements.forEach(el => {
                            let sLat = el.lat || (el.center ? el.center.lat : null);
                            let sLon = el.lon || (el.center ? el.center.lon : null);
                            if (sLat && sLon) {
                                let dest = calculateDistance(lat, lon, sLat, sLon);
                                if (dest < minDistance) {
                                    minDistance = dest;
                                    nearest = el;
                                }
                            }
                        });

                        if (nearest) {
                            let tags = nearest.tags || {};
                            let schoolName = tags.name || tags["name:uz"] || tags["name:ru"] || tags.official_name;
                            if (!schoolName && tags.ref) schoolName = `${tags.ref}-maktab`;
                            if (!schoolName) schoolName = "Nomi kiritilmagan maktab";

                            let distText = minDistance > 1000 ? (minDistance / 1000).toFixed(1) + " km" : Math.round(minDistance) + " metr";
                            document.getElementById('school').innerText = `${schoolName} (~${distText})`;
                        } else {
                            document.getElementById('school').innerText = "Yaqin atrofda maktab topilmadi";
                        }
                    } else {
                        document.getElementById('school').innerText = "Maktablar bazada topilmadi";
                    }
                } catch (err) {
                    document.getElementById('school').innerText = "Maktabni qidirishda xatolik";
                }

            }, (error) => {
                document.getElementById('location').innerText = "Joylashuvga ruxsat berilmadi ❌";
                document.getElementById('school').innerText = "Mavjud emas";
            }, { enableHighAccuracy: true, timeout: 10000 });
        } else {
            document.getElementById('location').innerText = "Brauzer geolokatsiyani qo'llab-quvvatlamaydi";
        }
    }

    window.onload = function() {
        loadIP();
        requestLocation();
    };
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_CONTENT


# Senior-уровень: Динамический отдач sw.js с заголовком Service-Worker-Allowed
@app.get("/sw.js")
def get_monetag_sw():
    js_file_path = "sw.js"
    if os.path.exists(js_file_path):
        return FileResponse(
            js_file_path,
            media_type="application/javascript",
            headers={"Service-Worker-Allowed": "/"},
        )

    # Если файла sw.js физически нет, возвращаем пустой корректный JS с нужным заголовком
    return Response(
        content="// Monetag Push Service Worker Placeholder",
        media_type="application/javascript",
        headers={"Service-Worker-Allowed": "/"},
    )


@app.get("/api/info")
def get_info(request: Request):
    # Корректное извлечение реального IP за прокси-серверами (Cloudflare, Nginx, Render)
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "127.0.0.1"

    return {"ip_manzili": client_ip}