import requests
from requests.auth import HTTPBasicAuth

# الإعدادات
base_url = "http://localhost:8069"
auth = HTTPBasicAuth('admin', 'admin')


def test_api(title, params=None):
    """دالة مساعدة للتيست"""
    print(f"\n{'=' * 60}")
    print(f"🧪 {title}")
    print(f"{'=' * 60}")

    response = requests.get(f"{base_url}/v1/property", params=params, auth=auth)
    data = response.json()

    if data['status'] == 'success':
        print(f"✅ Status: Success")
        print(f"📊 Total Items: {data['pagination']['total_items']}")
        print(f"📄 Page: {data['pagination']['page']} of {data['pagination']['total_pages']}")
        print(f"📋 Items in this page: {data['pagination']['items_in_page']}")

        if data.get('filters'):
            print(f"🔍 Active Filters: {[k for k, v in data['filters'].items() if v]}")

        if data.get('sorting'):
            print(f"📊 Sorting: {data['sorting']['field']} ({data['sorting']['order']})")

        # عرض أول 3 نتائج
        if data['data']:
            print(f"\n📝 Sample Results:")
            for prop in data['data'][:3]:
                print(f"   - {prop['name']} | Price: {prop['expected_price']} | Bedrooms: {prop['bedrooms']}")
    else:
        print(f"❌ Error: {data.get('message')}")

    return data


# ============================================
# 1️⃣ تيست Pagination (التقسيم لصفحات)
# ============================================

print("\n" + "🔷" * 30)
print("1️⃣ PAGINATION TESTS")
print("🔷" * 30)

# الصفحة الأولى (أول 2 عناصر)
test_api("Page 1 - First 2 items", {'page': 1, 'limit': 2})

# الصفحة الثانية
test_api("Page 2 - Next 2 items", {'page': 2, 'limit': 2})

# الصفحة الثالثة
test_api("Page 3 - Next 2 items", {'page': 3, 'limit': 2})

# ============================================
# 2️⃣ تيست Sorting (الترتيب)
# ============================================

print("\n" + "🔷" * 30)
print("2️⃣ SORTING TESTS")
print("🔷" * 30)

# ترتيب حسب السعر تصاعدي (من الأرخص)
test_api("Sort by Price - Ascending (Cheapest first)",
         {'sort': 'expected_price', 'order': 'asc'})

# ترتيب حسب السعر تنازلي (من الأغلى)
test_api("Sort by Price - Descending (Most expensive first)",
         {'sort': 'expected_price', 'order': 'desc'})

# ترتيب حسب عدد الغرف
test_api("Sort by Bedrooms - Descending",
         {'sort': 'bedrooms', 'order': 'desc'})

# ترتيب حسب الاسم أبجدياً
test_api("Sort by Name - Alphabetically",
         {'sort': 'name', 'order': 'asc'})

# ============================================
# 3️⃣ تيست Range Filters (فلترة بالنطاق)
# ============================================

print("\n" + "🔷" * 30)
print("3️⃣ RANGE FILTER TESTS")
print("🔷" * 30)

# عقارات سعرها من 100k لـ 400k
test_api("Price Range: 100,000 - 400,000",
         {'price_min': 100000, 'price_max': 400000})

# عقارات فيها من 3 لـ 5 أوضة
test_api("Bedrooms Range: 3-5",
         {'bedrooms_min': 3, 'bedrooms_max': 5})

# عقارات سعرها أكثر من 300k
test_api("Price > 300,000",
         {'price_min': 300000})

# عقارات فيها 4 أوضة أو أقل
test_api("Bedrooms <= 4",
         {'bedrooms_max': 4})

# ============================================
# 4️⃣ تيست Search (البحث النصي)
# ============================================

print("\n" + "🔷" * 30)
print("4️⃣ TEXT SEARCH TESTS")
print("🔷" * 30)

# البحث عن "villa"
test_api("Search for 'villa'",
         {'search': 'villa'})

# البحث عن "copy"
test_api("Search for 'copy'",
         {'search': 'copy'})

# البحث عن postcode "88"
test_api("Search for postcode '88'",
         {'search': '88'})

# ============================================
# 5️⃣ تيست مجمع (كل الميزات معاً)
# ============================================

print("\n" + "🔷" * 30)
print("5️⃣ COMBINED FEATURES TEST")
print("🔷" * 30)

# عقارات draft + سعرها أقل من 400k + مرتبة حسب السعر + الصفحة الأولى
test_api("Complex Query: Draft properties, price < 400k, sorted by price, page 1",
         {
             'state': 'draft',
             'price_max': 400000,
             'sort': 'expected_price',
             'order': 'asc',
             'page': 1,
             'limit': 5
         })

# عقارات فيها 4+ أوضة + مرتبة حسب عدد الغرف
test_api("Properties with 4+ bedrooms, sorted by bedrooms DESC",
         {
             'bedrooms_min': 4,
             'sort': 'bedrooms',
             'order': 'desc'
         })

# ============================================
# 6️⃣ تيست الـ Edge Cases
# ============================================

print("\n" + "🔷" * 30)
print("6️⃣ EDGE CASES TESTS")
print("🔷" * 30)

# صفحة غير موجودة
test_api("Non-existent page (page 100)", {'page': 100, 'limit': 10})

# limit كبير جداً (يجب أن يُحد إلى 100)
test_api("Very large limit (should cap at 100)", {'limit': 9999})

# بحث عن شيء غير موجود
test_api("Search for non-existent term", {'search': 'xyz123abc'})

# نطاق سعر غير منطقي (min > max)
test_api("Illogical price range (min > max)",
         {'price_min': 500000, 'price_max': 100000})

# ============================================
# ملخص نهائي
# ============================================

print("\n" + "=" * 60)
print("✅ ALL TESTS COMPLETED!")
print("=" * 60)
print("\n📚 Features Tested:")
print("   ✅ Pagination (page, limit)")
print("   ✅ Sorting (sort, order)")
print("   ✅ Range Filters (price_min/max, bedrooms_min/max)")
print("   ✅ Text Search (search)")
print("   ✅ Combined Queries")
print("   ✅ Edge Cases")
print("=" * 60)