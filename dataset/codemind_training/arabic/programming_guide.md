# دليل برمجي تطبيقي: بايثون وجافاسكربت والويب

## البحث الثنائي والفرز

البحث الثنائي خوارزمية للعثور على قيمة داخل قائمة مرتبة. تبدأ الخوارزمية من العنصر الأوسط، ثم تستبعد نصف المجال في كل خطوة. لذلك ينخفض عدد المقارنات من رتبة $n$ إلى رتبة $\log_2(n)$. يشترط أن تكون البيانات مرتبة مسبقاً؛ تطبيق البحث الثنائي على قائمة غير مرتبة قد يعيد نتيجة خاطئة حتى لو كان الكود صحيحاً من ناحية الصياغة.

```python
from dataset.codemind_training.python.core_algorithms import binary_search

numbers = [3, 8, 12, 19, 27, 31]
position = binary_search(numbers, 19)
print(position)
```

فرز الفقاعات مناسب للتعلم وفهم المقارنة والتبديل، لكنه ليس اختياراً جيداً لقوائم كبيرة لأن زمنه في الحالة العامة تربيعي $O(n^2)$. أما فرز الدمج فيقسّم القائمة إلى أجزاء، ويرتب الأجزاء، ثم يدمجها بترتيب صحيح. زمنه $O(n \log n)$ ويحتاج مساحة إضافية. في تطبيق بايثون اعتيادي، `list.sort()` أو `sorted()` أفضل غالباً لأنهما يستخدمان خوارزمية Timsort المحسّنة.

## الرسم البياني ودijkstra

يمثل الرسم البياني شبكة من العقد والحواف. في قاموس المجاورة المستخدم هنا، المفتاح هو العقدة، والقيمة قاموس يربط الجيران بأوزان الحواف. خوارزمية Dijkstra تختار في كل مرة العقدة غير المزارة ذات المسافة المعروفة الأصغر، ثم تحاول تحسين مسافات جيرانها. لا تصلح الأوزان السالبة؛ وجود وزن سالب يستدعي خوارزمية أخرى مثل Bellman-Ford.

```python
from dataset.codemind_training.python.core_algorithms import dijkstra, reconstruct_path

graph = {
    "المكتبة": {"الميدان": 4, "المتحف": 2},
    "الميدان": {"المحطة": 5},
    "المتحف": {"الميدان": 1, "المحطة": 8},
    "المحطة": {},
}
distances, previous = dijkstra(graph, "المكتبة")
print(distances["المحطة"])  # 8
print(reconstruct_path(previous, "المحطة"))
```

تستعمل الشيفرة التعليمية بحثاً خطياً لاختيار أقل مسافة بين العقد غير المزارة، ولذلك يكون أداؤها $O(V^2 + E)$. في رسم كبير، تُستخدم عادةً طابور أولوية لتقليل الكلفة إلى ما يقارب $O((V + E) \log V)$.

## هياكل البيانات

القائمة المرتبطة تتكون من عقد تحمل قيمة ومؤشراً إلى العقدة التالية. الإضافة إلى الرأس أو الذيل سريعة، لكن الوصول إلى العنصر رقم مئة يتطلب المرور عبر العناصر السابقة. الشجرة الثنائية للبحث تحتفظ بقيم أصغر يسار العقدة وقيم أكبر أو مساوية يمينها. إذا لم تكن متوازنة، فقد تتحول إلى سلسلة ويصبح البحث خطياً.

المكدس يعمل بمبدأ «آخر عنصر يدخل هو أول عنصر يخرج» (LIFO)، وهو مفيد لسجل التراجع واستدعاءات الدوال. الطابور يعمل بمبدأ «أول عنصر يدخل هو أول عنصر يخرج» (FIFO)، ويناسب قوائم الانتظار والمهام. تنفيذ الطابور عبر `deque` يجعل السحب من الطرف الأمامي ثابت الزمن تقريباً، بخلاف حذف أول عنصر من قائمة بايثون.

```python
from dataset.codemind_training.python.core_algorithms import LinkedList, Queue, Stack

history = Stack[str]()
history.push("صفحة البداية")
history.push("صفحة المقال")
print(history.pop())

jobs = Queue[str]()
jobs.enqueue("إرسال التقرير")
print(jobs.dequeue())

names = LinkedList[str]()
names.append("ليلى")
names.prepend("عمر")
print(list(names))
```

## البرمجة الكائنية وأنماط التصميم

التغليف يجمع الحالة والعمليات المتعلقة بها في كائن، والوراثة تسمح ببناء نوع متخصص انطلاقاً من نوع أعم، وتعدد الأشكال يسمح باستدعاء واجهة مشتركة على أنواع مختلفة. لا حاجة إلى الوراثة لمجرد إعادة استخدام بضعة أسطر؛ غالباً تكون الدوال والتركيب أوضح.

نمط Singleton يقيّد إنشاء كائن إلى نسخة مشتركة. قد يكون مفيداً لإعدادات العملية الواحدة، لكنه يضيف حالة عالمية ويجعل الاختبارات أكثر تعقيداً. إذا احتجت إعدادات متعددة أو عزلاً بين الاختبارات، مرّر كائن الإعدادات إلى الدوال بدلاً من الاعتماد على Singleton.

نمط Factory يخفي تفاصيل إنشاء الكائن. يطلب المستهلك قناة الإشعار من المصنع، والمصنع يعيد التنفيذ المناسب. تصبح إضافة قناة جديدة أقل ارتباطاً بالكود المستهلك، ويمكن رفض الأنواع غير المدعومة برسالة واضحة.

```python
from dataset.codemind_training.python.core_algorithms import ApplicationSettings, NotificationFactory

first = ApplicationSettings("production")
second = ApplicationSettings("test")
assert first is second

sender = NotificationFactory.create("email")
print(sender.send("اكتمل النسخ الاحتياطي"))
```

## الملفات وقواعد البيانات والأخطاء

استخدم مدير السياق `with open(...)` حتى يُغلق الملف عند النجاح أو الفشل. عند قراءة JSON، عالج أخطاء النظام وأخطاء التحليل، ولا تفترض أن الملف موجود أو سليم. الكتابة الذرية تكتب إلى ملف مؤقت ثم تستبدل الملف الهدف، فتقلل احتمال بقاء ملف جزئي بعد انقطاع البرنامج.

```python
from pathlib import Path
from dataset.codemind_training.python.core_algorithms import DataAccessError, read_json, write_json_atomically

settings_path = Path("runtime/settings.json")
write_json_atomically(settings_path, {"language": "ar", "debug": False})
try:
    settings = read_json(settings_path)
except DataAccessError as error:
    print(f"تعذرت قراءة الإعدادات: {error}")
```

تأتي SQLite مع بايثون ولا تحتاج إلى خادم منفصل. مرّر القيم إلى SQL باستخدام العناصر النائبة `?`؛ لا تركّب استعلاماً بإدخال النص مباشرة، لأن ذلك يفتح باب حقن SQL. مدير سياق اتصال SQLite ينفذ المعاملة عند الخروج بنجاح ويلغيها عند حدوث استثناء.

```python
from dataset.codemind_training.python.core_algorithms import add_task, create_task_database, list_tasks, mark_task_completed

database_path = "runtime/tasks.sqlite3"
create_task_database(database_path)
task_id = add_task(database_path, "مراجعة طلبات الفريق")
mark_task_completed(database_path, task_id)
print(list_tasks(database_path))
```

## جافاسكربت غير المتزامنة والواجهات

`async` و`await` يجعلان تدفق الطلب الشبكي مقروءاً، لكنهما لا يلغيان احتمال فشل الشبكة. `fetch` لا يرفض الوعد تلقائياً عند استجابة HTTP مثل 404، لذلك افحص `response.ok`. افحص نوع المحتوى قبل تحليل JSON، واعرض رسالة مناسبة عند غياب الشبكة أو وجود استجابة غير صالحة.

```javascript
async function showPost(postId) {
  const response = await fetch(`https://jsonplaceholder.typicode.com/posts/${postId}`);
  if (!response.ok) {
    throw new Error(`فشل الطلب برمز ${response.status}`);
  }
  const post = await response.json();
  return { title: post.title, preview: post.body.slice(0, 80) };
}

showPost(1)
  .then((post) => console.log(post.title))
  .catch((error) => console.error("تعذر تحميل المقال:", error.message));
```

إدارة الحالة البسيطة تحفظ الحالة في مكان واحد، وتبلغ المشتركين عند تحديثها. يجب ألا يُعدّل المستهلك كائن الحالة الأصلي من الخارج؛ لهذا يعيد مثال `Store` نسخة من الحالة. عند بناء تطبيق أكبر، استخدم مكتبة حالة مناسبة للنظام بدلاً من توسيع مخزن يدوي بلا حدود.

في DOM، أنشئ العناصر باستخدام `document.createElement` وأضف مستمعاً واحداً للأحداث في الحاوية عندما تتكرر العناصر. هذا النمط يسمى تفويض الأحداث، ويظل يعمل بعد إعادة رسم القائمة. إذا أدخلت قيمة مستخدم في `innerHTML`، فاهرب المحارف الخاصة أولاً أو استخدم `textContent` لبناء النص. لا تعامل بيانات المستخدم على أنها HTML موثوق.

## map وfilter وreduce

`map` يحول كل عنصر إلى قيمة جديدة مع الحفاظ على عدد العناصر. `filter` يحتفظ بالعناصر التي تحقق شرطاً. `reduce` يجمع العناصر في قيمة نهائية مثل مجموع أو إحصاء. افصل هذه الخطوات حين يحسن ذلك القراءة، وتجنب `reduce` المتداخل الذي يخفي الغرض من المعالجة.

```javascript
const orders = [
  { customer: "سارة", total: 35, paid: true },
  { customer: "رامي", total: 18, paid: false },
  { customer: "سارة", total: 42, paid: true },
];

const paidTotalsByCustomer = orders
  .filter((order) => order.paid)
  .map((order) => ({ ...order, total: Number(order.total) }))
  .reduce((totals, order) => {
    totals[order.customer] = (totals[order.customer] ?? 0) + order.total;
    return totals;
  }, {});

console.log(paidTotalsByCustomer);
```

## HTML وCSS وTailwind

HTML الدلالي يعطي الصفحة بنية مفهومة لمتصفح وقارئ شاشة ومحرك بحث. استخدم `header` و`nav` و`main` و`section` و`footer` وفق وظيفة المحتوى. اربط كل حقل نموذج بعنصر `label`، وسمِّ أزرار الأيقونات عبر `aria-label`، واجعل للجداول رؤوس أعمدة تستخدم `scope="col"`.

Tailwind CSS يوفر فئات صغيرة لتركيب التخطيط والمسافات والألوان مباشرة في HTML. التصميم المتجاوب يبدأ عادةً بتخطيط العمود الواحد، ثم تضاف نقاط التحول مثل `md:` و`lg:` للشاشات الأوسع. وجود CDN مناسب لتجربة تعليمية مستقلة، لكنه ليس بديلاً عن إعداد بناء Tailwind في الإنتاج؛ البناء الإنتاجي يزيل الفئات غير المستخدمة ويثبت إصدار الحزمة.

صفحة الهبوط في `../web/landing_page.html` تستخدم صوراً فعلية ونقاط توقف للشاشات الصغيرة. لوحة `../web/analytics_dashboard.html` تعرض مؤشرات وجدولاً قابلاً للبحث وتصديراً إلى CSV. صفحة `../web/auth_forms.html` تبدّل بين تسجيل الدخول وإنشاء الحساب وتتحقق من الحقول في المتصفح، لكنها لا تصادق المستخدم ولا تنشئ حساباً دون ربطها بخدمة خادمية آمنة.

## شروحات عامية برمجية

### كيف أسوي دالة في بايثون؟

اكتب `def` وبعدها اسم الدالة، وحط المدخلات بين القوسين. إذا الدالة بتحسب نتيجة، رجّعها بـ `return`. مثلاً:

```python
def calculate_total(price: float, quantity: int) -> float:
    if price < 0 or quantity < 0:
        raise ValueError("السعر والكمية لازم يكونون صفر أو أكثر")
    return price * quantity


print(calculate_total(12.5, 3))
```

لو استخدمت `print` داخل الدالة بس، فأنت عرضت النتيجة على الشاشة وما رجّعتها للمكان اللي نادى الدالة. استخدام `return` يخلي الكود يقدر يخزن الناتج أو يمرره لدالة ثانية.

### كيف أحل مشكلة الأخطاء في الكود؟

أول شي اقرأ آخر سطر من رسالة الخطأ، لأنه غالباً يحدد نوع المشكلة. بعدها طالع اسم الملف والسطر، وتأكد من القيم اللي وصلت للدالة. جرّب أصغر مثال يعيد المشكلة، وحط `assert` على النتيجة المتوقعة. لا تحط `try/except` عام وتكمل كأن كل شي تمام؛ عالج الاستثناء اللي تتوقعه واعرض سياق يساعدك تفهم السبب.

```python
def average(values: list[float]) -> float:
    if not values:
        raise ValueError("ما نقدر نحسب متوسط قائمة فاضية")
    return sum(values) / len(values)


try:
    result = average([])
except ValueError as error:
    print(f"تأكد من المدخلات: {error}")
```

### اشرح لي الخوارزمية ببساطة

تخيل عندك قاموس أسماء مرتب وتدور على اسم. بدل ما تبدأ من أول صفحة وتعد صفحة صفحة، افتح من النص. إذا الاسم اللي ظهر يسبق الاسم المطلوب، تجاهل النصف الأول؛ وإذا يتأخر عنه، تجاهل النصف الثاني. كرر الحركة على الجزء الباقي. كل مرة تقل الصفحات تقريباً للنصف، وهذا هو سبب سرعة البحث الثنائي. بس انتبه: لازم القاموس يكون مرتب من البداية.

### كيف أسوي طلب Fetch وأتعامل مع JSON؟

حط الطلب داخل `try` أو أضف `.catch`، وافحص `response.ok` قبل `response.json()`. لو السيرفر رجع 404، `fetch` عادةً يرجع استجابة عادية وما يرمي خطأ من نفسه. بعدين اعرض رسالة مفهومة للمستخدم بدل ما تترك الصفحة معلقة.

```javascript
async function loadProfile() {
  try {
    const response = await fetch("/api/profile");
    if (!response.ok) throw new Error(`رمز الخادم ${response.status}`);
    const profile = await response.json();
    document.querySelector("#profile-name").textContent = profile.name;
  } catch (error) {
    document.querySelector("#profile-status").textContent = `ما قدرنا نحمل الملف: ${error.message}`;
  }
}
```

## أسئلة وأجوبة تدريبية

**س: متى أختار Stack ومتى أختار Queue؟**

ج: اختر Stack لما تحتاج ترجع لآخر شي أضفته أولاً، مثل التراجع عن تعديل. اختر Queue لما تبي تعالج العناصر بترتيب وصولها، مثل قائمة مهام منتظرة.

**س: هل Dijkstra تصلح إذا عندي أوزان سالبة؟**

ج: لا. خوارزمية Dijkstra تفترض أن الأوزان غير سالبة، لأن تثبيت أقصر مسافة لعقدة ثم اكتشاف طريق أرخص عبر وزن سالب يكسر هذا الافتراض. استخدم Bellman-Ford إذا كانت الأوزان السالبة مطلوبة، وتحقق من وجود دورة سالبة.

**س: ليش أفحص `response.ok` بعد `fetch`؟**

ج: لأن `fetch` يرفض الوعد عادةً عند فشل الشبكة، لكنه لا يرفضه لمجرد أن حالة HTTP هي 404 أو 500. فحص `ok` يميز استجابة ناجحة عن استجابة HTTP فاشلة قبل محاولة استخدام بياناتها.

**س: هل صفحة الدخول في هذا المثال آمنة للإنتاج؟**

ج: لا. التحقق في المتصفح لتحسين تجربة الاستخدام فقط ويمكن تجاوزه. يجب أن يتحقق الخادم من بيانات الاعتماد، ويحمي الجلسة والطلبات، ويخزن كلمات المرور بتجزئة مناسبة، ويطبق حدود المحاولات وسياسات الاستعادة.