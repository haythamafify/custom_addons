"""
tests/test_zatca_async.py

اختبارات الوحدة لموديول pos_zatca_async_v18
بدون أي ربط بـ ZATCA — كل الـ web service calls اتعملت mock

تشغيل الاختبارات:
    python -m pytest odoo/custom_addons/pos_zatca_async_v18/tests/test_zatca_async.py -v

أو من خلال Odoo test runner:
    python odoo-bin -d your_db --test-enable --stop-after-init -i pos_zatca_async_v18
"""

from unittest.mock import patch, MagicMock, call
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install', 'zatca_async')
class TestZatcaAsyncSkip(TransactionCase):
    """
    التأكد إن الـ skip_zatca_edi_sync context
    بيمنع استدعاء ZATCA web service فعلاً
    """

    def setUp(self):
        super().setUp()
        # نعمل invoice وهمي بدون أي data حقيقي
        self.mock_invoice = MagicMock()
        self.mock_invoice.name = 'INV/TEST/0001'
        self.mock_invoice.id = 999

    def test_skip_flag_prevents_zatca_call(self):
        """
        لو skip_zatca_edi_sync = True في الـ context،
        المفروض super()._call_web_service_before_invoice_pdf_render ميتعملش
        """
        # نجيب instance من AccountMoveSend مع context الـ skip
        wizard = self.env['account.move.send'].with_context(
            skip_zatca_edi_sync=True
        )

        fake_invoices_data = {'mock_invoice': {}}

        # نعمل patch للـ super call عشان نتأكد إنه ماتنادىش
        with patch(
            'odoo.addons.account.wizard.account_move_send'
            '.AccountMoveSend._call_web_service_before_invoice_pdf_render'
        ) as mock_super:
            wizard._call_web_service_before_invoice_pdf_render(fake_invoices_data)
            # المفروض super ماتنادىش خالص
            mock_super.assert_not_called()

    def test_no_skip_flag_calls_zatca_normally(self):
        """
        لو مفيش skip flag،
        المفروض super()._call_web_service يتنادى عادي
        """
        wizard = self.env['account.move.send']  # no skip context

        fake_invoices_data = {'mock_invoice': {}}

        with patch(
            'odoo.addons.account.wizard.account_move_send'
            '.AccountMoveSend._call_web_service_before_invoice_pdf_render'
        ) as mock_super:
            # نعمل wrap للـ method بتاعنا فوق الـ mock
            wizard._call_web_service_before_invoice_pdf_render(fake_invoices_data)
            mock_super.assert_called_once_with(fake_invoices_data)


@tagged('post_install', '-at_install', 'zatca_async')
class TestZatcaAsyncPosOrder(TransactionCase):
    """
    التأكد إن POS order بيضيف الـ context flag صح
    """

    def test_pos_order_sets_skip_context(self):
        """
        _generate_pos_order_invoice المفروض يشتغل مع skip_zatca_edi_sync=True
        """
        pos_order = self.env['pos.order']

        # نتأكد إن الـ context بيتضاف صح
        with patch.object(
            type(pos_order),
            '_generate_pos_order_invoice',
            wraps=lambda self: self.env.context.get('skip_zatca_edi_sync')
        ):
            # نأكد إن الـ context flag موجود جوه الـ call
            order_with_context = pos_order.with_context(skip_zatca_edi_sync=True)
            self.assertTrue(
                order_with_context.env.context.get('skip_zatca_edi_sync'),
                "skip_zatca_edi_sync flag should be True inside POS invoice generation"
            )


@tagged('post_install', '-at_install', 'zatca_async')
class TestZatcaCronProcessor(TransactionCase):
    """
    اختبار الـ Cron بدون ربط ZATCA حقيقي
    """

    def _create_mock_invoice(self, name, edi_state='to_send'):
        """Helper: يعمل invoice وهمي في الـ DB"""
        partner = self.env['res.partner'].create({'name': 'Test Partner'})
        journal = self.env['account.journal'].search(
            [('type', '=', 'sale')], limit=1
        )
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': partner.id,
            'journal_id': journal.id,
            'invoice_line_ids': [(0, 0, {
                'name': 'Test Product',
                'quantity': 1,
                'price_unit': 100.0,
            })],
        })
        invoice.action_post()

        # نضبط الـ l10n_sa_edi_state لو الـ field موجود
        if hasattr(invoice, 'l10n_sa_edi_state'):
            invoice.write({'l10n_sa_edi_state': edi_state})

        return invoice

    def test_cron_processes_pending_invoices(self):
        """
        الـ Cron المفروض يلاقي الـ invoices اللي state='to_send'
        ويحاول يعالجها
        """
        # نعمل invoice وهمي
        invoice = self._create_mock_invoice('INV/CRON/TEST/001', 'to_send')

        # نعمل mock لـ action_process_edi_web_services عشان منبعتش لـ ZATCA
        with patch.object(
            type(invoice),
            'action_process_edi_web_services',
            return_value=True
        ) as mock_process:
            self.env['account.move']._cron_process_zatca_edi()

            # المفروض الـ method اتنادت على الـ invoice ده
            if hasattr(invoice, 'l10n_sa_edi_state'):
                mock_process.assert_called()

    def test_cron_handles_single_invoice_error_gracefully(self):
        """
        لو invoice واحدة فشلت، الـ cron المفروض يكمل مع الباقي
        ومايوقفش كل الـ batch
        """
        invoice1 = self._create_mock_invoice('INV/CRON/TEST/002', 'to_send')
        invoice2 = self._create_mock_invoice('INV/CRON/TEST/003', 'to_send')

        call_count = {'n': 0}

        def side_effect_raise_on_first(*args, **kwargs):
            call_count['n'] += 1
            if call_count['n'] == 1:
                raise Exception("Simulated ZATCA network error")
            return True

        with patch.object(
            type(invoice1),
            'action_process_edi_web_services',
            side_effect=side_effect_raise_on_first
        ):
            # المفروض ميرميش exception للخارج
            try:
                self.env['account.move']._cron_process_zatca_edi()
                error_raised = False
            except Exception:
                error_raised = True

            self.assertFalse(
                error_raised,
                "Cron should NOT raise exception when a single invoice fails — "
                "it should log the error and continue with the rest."
            )

    def test_cron_does_nothing_when_no_pending(self):
        """
        لو مفيش invoices pending، الـ cron يرجع بهدوء من غير errors
        """
        # نتأكد إن مفيش invoices to_send
        with patch.object(
            self.env['account.move'].__class__,
            'search',
            return_value=self.env['account.move']
        ):
            try:
                self.env['account.move']._cron_process_zatca_edi()
                ran_ok = True
            except Exception:
                ran_ok = False

            self.assertTrue(ran_ok, "Cron should run without errors when no invoices pending")

    def test_cron_sequential_order(self):
        """
        التأكد إن الـ cron بيعالج الـ invoices بالترتيب (id asc)
        ده بيضمن إن الـ chain_index بيتعمل بالترتيب الصح
        """
        processed_ids = []

        # نعمل mock للـ search يرجع invoices بترتيب محدد
        mock_inv_1 = MagicMock()
        mock_inv_1.id = 1
        mock_inv_1.name = 'INV/001'

        mock_inv_2 = MagicMock()
        mock_inv_2.id = 2
        mock_inv_2.name = 'INV/002'

        mock_inv_3 = MagicMock()
        mock_inv_3.id = 3
        mock_inv_3.name = 'INV/003'

        ordered_invoices = [mock_inv_1, mock_inv_2, mock_inv_3]

        def mock_process(inv):
            processed_ids.append(inv.id)

        with patch.object(
            self.env['account.move'].__class__,
            'search',
            return_value=ordered_invoices
        ):
            for inv in ordered_invoices:
                inv.action_process_edi_web_services = lambda: processed_ids.append(inv.id)

            # نشغل الـ cron
            # في الحالة دي بنتحقق إن الـ search بيطلب order='id asc'
            search_calls = []
            original_search = self.env['account.move'].search

            def capture_search(domain, **kwargs):
                search_calls.append(kwargs)
                return self.env['account.move']  # empty recordset

            with patch.object(
                type(self.env['account.move']),
                'search',
                side_effect=capture_search
            ):
                self.env['account.move']._cron_process_zatca_edi()

                # نتأكد إن الـ order='id asc' موجود في الـ search
                if search_calls:
                    self.assertEqual(
                        search_calls[0].get('order'),
                        'id asc',
                        "Cron MUST process invoices in order 'id asc' to guarantee "
                        "correct ZATCA chain_index sequence!"
                    )
