# pos_zatca_async — ZATCA EDI Async Fix for POS

## المشكلة اللي بيحلها الموديول ده

```
psycopg2.errors.SerializationFailure:
could not serialize access due to concurrent update
```

بتحصل وقت الزحمة في POS المطاعم لما أكتر من أوردر بيتبعتوا في نفس اللحظة.

---

## السبب الجذري

```
POS Transaction (open)
    └── _process_saved_order()
        └── _generate_pos_order_invoice()
            └── _generate_pdf_and_send_invoice()
                └── _call_web_service_before_invoice_pdf_render()
                    └── action_process_edi_web_services()
                        └── _l10n_sa_post_zatca_edi()
                            └── _l10n_sa_edi_get_next_chain_index()
                                └── ir.sequence
                                    └── SELECT ... FOR UPDATE NOWAIT  💥
```

الـ `FOR UPDATE NOWAIT` بيعمل lock على الـ sequence row،
لو اتنين order وصلوا مع بعض → واحد منهم بيتطرد فوراً بدل ما يستنى.

---

## الحل

```
قبل الموديول:
POS → Invoice → [chain_index LOCK] → ZATCA  ← كل ده جوه نفس الـ transaction

بعد الموديول:
POS → Invoice فقط  ✅ سريع، مفيش lock
              ↓
        Cron (كل 5 دقايق)
              ↓
        chain_index + ZATCA  ✅ sequential، مفيش concurrency
```

---

## التركيب

```bash
# انسخ الموديول في مجلد addons بتاعك
cp -r pos_zatca_async /path/to/your/addons/

# في Odoo: Settings → Activate Developer Mode
# Apps → Update Apps List
# ابحث عن "POS ZATCA Async" وثبّته
```

---

## الإعدادات بعد التثبيت

**Technical → Scheduled Actions → "ZATCA EDI: Process Pending Invoices (Async)"**

| Setting | Default | توصية للمطاعم |
|---------|---------|---------------|
| Interval | 5 minutes | 1-2 minutes |
| Batch Size | 50 invoices | زوّدها لو حجم عالي |

---

## ملاحظة مهمة

بعد تثبيت الموديول، الفاتورة هتتعمل فوراً وقت الدفع ✅
لكن الإرسال لـ ZATCA هيتأخر بالكتير 5 دقايق.

ده مقبول قانونياً (ZATCA بتسمح بفترة إرسال معقولة).
لو محتاج تأكد، راجع مع المحاسب/المستشار القانوني.

---

## الملفات

```
pos_zatca_async/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── pos_order.py       ← skip ZATCA sync من الـ POS transaction
│   └── account_move.py    ← cron logic + batch processor
└── data/
    └── ir_cron.xml        ← الـ scheduled action
```
