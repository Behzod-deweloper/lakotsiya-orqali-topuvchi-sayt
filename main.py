from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

HTML_CONTENT = r"""
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aniq Joylashuv va Eng Yaqin Maktab</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
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
    <div class="info">Aniq Manzil: <span id="location">GPS kutilmoqda...</span></div>
    <div class="info">Eng Yaqin Maktab: <span id="school">Qidirilmoqda...</span></div>
    <div class="info">Qurilma Nomi: <span id="device-model">Aniqlanmoqda...</span></div>
    <div class="info">Versiya: <span id="os-version">Aniqlanmoqda...</span></div>
</div>

<script>
    // Qurilma nomi va versiyasini to'g'ri aniqlash
    function getDeviceInfo() {
        const ua = navigator.userAgent;
        let model = "Android Qurilma";
        let version = "Android OS";

        // Android uchun
        if (/android/i.test(ua)) {
            let verMatch = ua.match(/Android\s([0-9\.]+)/i);
            if (verMatch) {
                version = "Android " + verMatch[1];
            }

            // Samsung va boshqa modellar uchun Build oldidagi yoki qavs ichidagi nomni to'g'ri olish
            let buildMatch = ua.match(/\s+([^\s]+)\s+Build\//);
            if (buildMatch && buildMatch[1].length > 1) {
                model = buildMatch[1];
            } else {
                let parts = ua.split(';');
                if (parts.length >= 2) {
                    let potentialModel = parts[parts.length - 2].trim();
                    if (potentialModel && !potentialModel.includes("Mobile") && !potentialModel.includes("Apple")) {
                        model = potentialModel;
                    }
                }
            }
        } 
        // iOS uchun
        else if (/iphone|ipad|ipod/i.test(ua)) {
            let verMatch = ua.match(/OS\s([0-9_]+)/i);
            version = verMatch ? "iOS " + verMatch[1].replace(/_/g, '.') : "iOS";
            model = /ipad/i.test(ua) ? "Apple iPad" : "Apple iPhone";
        } 
        else if (/windows/i.test(ua)) {
            model = "Windows PC";
            version = "Windows OS";
        } 
        else if (/macintosh|mac os x/i.test(ua)) {
            model = "Macintosh";
            version = "Mac OS";
        } 
        else if (/linux/i.test(ua)) {
            model = "Linux PC";
            version = "Linux OS";
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

    async function loadData() {
        try {
            let res = await fetch('/api/info');
            let data = await res.json();
            document.getElementById('ip').innerText = data.ip_manzili;

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(async (position) => {
                    let lat = position.coords.latitude;
                    let lon = position.coords.longitude;

                    // Manzilni aniqlash
                    try {
                        let geoRes = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1&accept-language=uz`);
                        let geoData = await geoRes.json();
                        let addr = geoData.address;

                        let parts = [];
                        if (addr.state || addr.region) parts.push(addr.state || addr.region);
                        if (addr.city || addr.town || addr.county) parts.push(addr.city || addr.town || addr.county);
                        if (addr.suburb || addr.district) parts.push(addr.suburb || addr.district);
                        if (addr.neighbourhood || addr.quarter) parts.push(addr.neighbourhood || addr.quarter);
                        if (addr.road) parts.push(addr.road + " ko'chasi");

                        document.getElementById('location').innerText = parts.length > 0 ? parts.join(", ") : "Topildi";
                    } catch (err) {
                        document.getElementById('location').innerText = "Manzilni aniqlab bo'lmadi";
                    }

                    // Maktabni qidirish
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
                }, { enableHighAccuracy: true });
            }
        } catch (e) {
            console.error(e);
        }
    }
    loadData();
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_CONTENT


@app.get("/api/info")
def get_info(request: Request):
    client_ip = request.headers.get("x-forwarded-for")
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = request.client.host
    return {"ip_manzili": client_ip}