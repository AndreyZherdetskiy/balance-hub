"""Тесты для Pydantic схем платежей - все сценарии."""

from __future__ import annotations

from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.schemas.payment import PaymentPublic, WebhookPayment
from tests.constants import (
    TestDomainConstraints,
    TestDomainIds,
    TestMonetaryConstants,
    TestNumericConstants,
    TestTransactionData,
)


class TestPaymentPublic:
    """Тесты для публичной схемы платежа."""

    def test_schema_valid(self) -> None:
        """Тест валидной публичной схемы платежа."""
        data = {
            "id": TestDomainIds.TEST_USER_ID,
            "transaction_id": TestDomainIds.TX_123,
            "user_id": TestDomainIds.TEST_USER_ID,
            "account_id": TestDomainIds.TEST_USER_ID,
            "amount": TestMonetaryConstants.AMOUNT_50_25,
        }

        payment_public = PaymentPublic(**data)
        assert payment_public.id == TestDomainIds.TEST_USER_ID
        assert payment_public.transaction_id == TestDomainIds.TX_123
        assert payment_public.user_id == TestDomainIds.TEST_USER_ID
        assert payment_public.account_id == TestDomainIds.TEST_USER_ID
        assert payment_public.amount == TestMonetaryConstants.AMOUNT_50_25

    def test_zero_amount(self) -> None:
        """Тест валидации нулевой суммы платежа."""
        data = {
            "id": TestDomainIds.TEST_USER_ID,
            "transaction_id": TestDomainIds.TX_123,
            "user_id": TestDomainIds.TEST_USER_ID,
            "account_id": TestDomainIds.TEST_USER_ID,
            "amount": TestMonetaryConstants.AMOUNT_0_00,
        }

        with pytest.raises(ValidationError) as exc_info:
            PaymentPublic(**data)

        errors = exc_info.value.errors()
        assert any("greater than 0" in str(error["msg"]) for error in errors)

    def test_negative_amount(self) -> None:
        """Тест валидации отрицательной суммы платежа."""
        data = {
            "id": TestDomainIds.TEST_USER_ID,
            "transaction_id": TestDomainIds.TX_123,
            "user_id": TestDomainIds.TEST_USER_ID,
            "account_id": TestDomainIds.TEST_USER_ID,
            "amount": TestMonetaryConstants.AMOUNT_NEG_10_00,
        }

        with pytest.raises(ValidationError) as exc_info:
            PaymentPublic(**data)

        errors = exc_info.value.errors()
        assert any("greater than 0" in str(error["msg"]) for error in errors)

    def test_very_large_amount(self) -> None:
        """Тест схемы с очень большой суммой платежа."""
        large_amount = TestMonetaryConstants.AMOUNT_999999999999999_99
        payment_public = PaymentPublic(
            id=TestDomainIds.TEST_USER_ID,
            transaction_id=TestDomainIds.TX_BIG,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=large_amount,
        )
        assert payment_public.amount == large_amount

    def test_very_small_amount(self) -> None:
        """Тест схемы с очень маленькой суммой платежа."""
        small_amount = TestMonetaryConstants.AMOUNT_0_01
        payment_public = PaymentPublic(
            id=TestDomainIds.TEST_USER_ID,
            transaction_id=TestDomainIds.TX_SMALL,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=small_amount,
        )
        assert payment_public.amount == small_amount

    def test_string_amount(self) -> None:
        """Тест схемы со строковым представлением суммы."""
        payment_public = PaymentPublic(
            id=TestDomainIds.TEST_USER_ID,
            transaction_id=TestDomainIds.TX_STRING,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_99_99_STR,  # type: ignore[arg-type]
        )
        assert payment_public.amount == TestMonetaryConstants.AMOUNT_99_99

    def test_very_long_transaction_id(self) -> None:
        """Тест валидации очень длинного transaction_id."""
        long_tx_id = TestDomainIds.LONG_TX_ID
        with pytest.raises(ValidationError) as exc_info:
            PaymentPublic(
                id=TestDomainIds.TEST_USER_ID,
                transaction_id=long_tx_id,
                user_id=TestDomainIds.TEST_USER_ID,
                account_id=TestDomainIds.TEST_USER_ID,
                amount=TestMonetaryConstants.AMOUNT_100_00,
            )
        errors = exc_info.value.errors()
        assert any("at most 64 characters" in str(error["msg"]) for error in errors)

    def test_unicode_transaction_id(self) -> None:
        """Тест схемы с Unicode transaction_id."""
        unicode_tx_id = TestDomainIds.UNICODE_TX_ID
        payment_public = PaymentPublic(
            id=TestDomainIds.TEST_USER_ID,
            transaction_id=unicode_tx_id,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
        )
        assert payment_public.transaction_id == unicode_tx_id

    def test_special_chars_transaction_id(self) -> None:
        """Тест схемы со специальными символами в transaction_id."""
        special_tx_id = TestDomainIds.SPECIAL_CHARS_TX_ID
        payment_public = PaymentPublic(
            id=TestDomainIds.TEST_USER_ID,
            transaction_id=special_tx_id,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
        )
        assert payment_public.transaction_id == special_tx_id

    def test_missing_required_fields(self) -> None:
        """Тест схемы с отсутствующими обязательными полями."""
        with pytest.raises(ValidationError):
            PaymentPublic(  # type: ignore[call-arg]
                transaction_id=TestDomainIds.TX_MISSING,
                user_id=TestDomainIds.TEST_USER_ID,
                account_id=TestDomainIds.TEST_USER_ID,
                amount=TestMonetaryConstants.AMOUNT_100_00,
            )

        with pytest.raises(ValidationError):
            PaymentPublic(  # type: ignore[call-arg]
                id=TestDomainIds.TEST_USER_ID,
                user_id=TestDomainIds.TEST_USER_ID,
                account_id=TestDomainIds.TEST_USER_ID,
                amount=TestMonetaryConstants.AMOUNT_100_00,
            )


class TestWebhookPayment:
    """Тесты для схемы вебхук платежа."""

    def test_schema_valid(self) -> None:
        """Тест валидной схемы вебхук платежа."""
        data = {
            "transaction_id": TestDomainIds.WEBHOOK_TX_1,
            "account_id": TestDomainIds.TEST_USER_ID,
            "user_id": TestDomainIds.TEST_USER_ID,
            "amount": TestMonetaryConstants.AMOUNT_100_00,
            "signature": "valid_signature_hash",
        }

        webhook_payment = WebhookPayment(**data)
        assert webhook_payment.transaction_id == TestDomainIds.WEBHOOK_TX_1
        assert webhook_payment.account_id == TestDomainIds.TEST_USER_ID
        assert webhook_payment.user_id == TestDomainIds.TEST_USER_ID
        assert webhook_payment.amount == TestMonetaryConstants.AMOUNT_100_00
        assert webhook_payment.signature == "valid_signature_hash"

    def test_empty_transaction_id(self) -> None:
        """Тест валидации пустого transaction_id."""
        data = {
            "transaction_id": "",
            "account_id": TestDomainIds.TEST_USER_ID,
            "user_id": TestDomainIds.TEST_USER_ID,
            "amount": TestMonetaryConstants.AMOUNT_100_00,
            "signature": "valid_signature_hash",
        }

        with pytest.raises(ValidationError) as exc_info:
            WebhookPayment(**data)

        errors = exc_info.value.errors()
        assert any("at least 1 character" in str(error["msg"]) for error in errors)

    def test_very_long_signature(self) -> None:
        """Тест схемы с очень длинной подписью."""
        long_signature = TestTransactionData.LONG_SIGNATURE
        webhook_payment = WebhookPayment(
            transaction_id=TestDomainIds.TX_LONG_SIG,
            account_id=TestDomainIds.TEST_USER_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature=long_signature,
        )
        assert webhook_payment.signature == long_signature

    def test_unicode_signature(self) -> None:
        """Тест схемы с Unicode подписью."""
        unicode_signature = TestTransactionData.UNICODE_SIGNATURE
        webhook_payment = WebhookPayment(
            transaction_id=TestDomainIds.TX_UNICODE_SIG,
            account_id=TestDomainIds.TEST_USER_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature=unicode_signature,
        )
        assert webhook_payment.signature == unicode_signature

    def test_hex_signature(self) -> None:
        """Тест схемы с hex подписью (как SHA256)."""
        hex_signature = TestTransactionData.HEX_SIGNATURE_EXAMPLE
        webhook_payment = WebhookPayment(
            transaction_id=TestDomainIds.TX_HEX_SIG,
            account_id=TestDomainIds.TEST_USER_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature=hex_signature,
        )
        assert webhook_payment.signature == hex_signature

    def test_negative_account_id(self) -> None:
        """Тест схемы с отрицательным account_id."""
        webhook_payment = WebhookPayment(
            transaction_id=TestDomainIds.TX_NEGATIVE_ACC,
            account_id=TestNumericConstants.NEGATIVE_ONE,
            user_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature="signature",
        )
        assert webhook_payment.account_id == TestNumericConstants.NEGATIVE_ONE

    def test_zero_account_id(self) -> None:
        """Тест схемы с нулевым account_id."""
        webhook_payment = WebhookPayment(
            transaction_id=TestDomainIds.TX_ZERO_ACC,
            account_id=TestNumericConstants.COUNT_EMPTY,
            user_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature="signature",
        )
        assert webhook_payment.account_id == TestNumericConstants.COUNT_EMPTY

    def test_large_ids(self) -> None:
        """Тест схемы с большими ID."""
        large_id = TestDomainConstraints.MAX_INT32
        webhook_payment = WebhookPayment(
            transaction_id=TestDomainIds.TX_LARGE_IDS,
            account_id=large_id,
            user_id=large_id,
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature="signature",
        )
        assert webhook_payment.account_id == large_id
        assert webhook_payment.user_id == large_id

    def test_string_ids(self) -> None:
        """Тест схемы со строковыми ID (должны конвертироваться)."""
        webhook_payment = WebhookPayment(
            transaction_id=TestDomainIds.TX_STRING_IDS,
            account_id=TestDomainIds.STR_ACC_ID_123,  # type: ignore[arg-type]
            user_id=TestDomainIds.STR_USER_ID_456,  # type: ignore[arg-type]
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature="signature",
        )
        assert webhook_payment.account_id == 123
        assert webhook_payment.user_id == 456

    def test_float_amount(self) -> None:
        """Тест схемы с float суммой."""
        webhook_payment = WebhookPayment(
            transaction_id=TestDomainIds.TX_FLOAT,
            account_id=TestDomainIds.TEST_USER_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            amount=99.99,  # type: ignore[arg-type]
            signature="signature",
        )
        assert webhook_payment.amount == Decimal("99.99")

    def test_int_amount(self) -> None:
        """Тест схемы с int суммой."""
        webhook_payment = WebhookPayment(
            transaction_id=TestDomainIds.TX_INT,
            account_id=TestDomainIds.TEST_USER_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            amount=100,  # type: ignore[arg-type]
            signature="signature",
        )
        assert webhook_payment.amount == Decimal("100")

    def test_missing_signature(self) -> None:
        """Тест схемы без подписи."""
        with pytest.raises(ValidationError):
            WebhookPayment(  # type: ignore[call-arg]
                transaction_id=TestDomainIds.TX_NO_SIG,
                account_id=TestDomainIds.TEST_USER_ID,
                user_id=TestDomainIds.TEST_USER_ID,
                amount=TestMonetaryConstants.AMOUNT_100_00,
            )
