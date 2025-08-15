"""Тесты для модели Payment - все сценарии."""

from __future__ import annotations

from app.models.payment import Payment
from tests.constants import (
    TestDomainConstraints,
    TestDomainIds,
    TestMonetaryConstants,
    TestNumericConstants,
)


class TestPaymentModel:
    """Тесты модели Payment."""

    def test_payment_model_creation(self) -> None:
        """Тест создания модели платежа."""
        payment = Payment(
            transaction_id=TestDomainIds.TEST_TX_1,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_50_25,
        )

        assert payment.transaction_id == TestDomainIds.TEST_TX_1
        assert payment.user_id == TestDomainIds.TEST_USER_ID
        assert payment.account_id == TestDomainIds.TEST_USER_ID
        assert payment.amount == TestMonetaryConstants.AMOUNT_50_25

    def test_payment_model_with_large_amount(self) -> None:
        """Тест модели платежа с большой суммой."""
        payment = Payment(
            transaction_id=TestDomainIds.TX_BIG,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_9999999999_99,
        )

        assert payment.amount == TestMonetaryConstants.AMOUNT_9999999999_99

    def test_payment_model_transaction_id_uniqueness(self) -> None:
        """Тест уникальности transaction_id в модели платежа."""
        payment1 = Payment(
            transaction_id=TestDomainIds.UNIQUE_TX_1,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_10_00,
        )

        payment2 = Payment(
            transaction_id=TestDomainIds.UNIQUE_TX_2,
            user_id=TestDomainIds.TEST_USER_ID_NEXT,
            account_id=TestDomainIds.TEST_USER_ID_NEXT,
            amount=TestMonetaryConstants.AMOUNT_20_00,
        )

        assert payment1.transaction_id != payment2.transaction_id

    def test_payment_model_very_long_transaction_id(self) -> None:
        """Тест модели платежа с очень длинным transaction_id."""
        long_tx_id = TestDomainIds.LONG_TX_ID
        payment = Payment(
            transaction_id=long_tx_id,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
        )

        assert payment.transaction_id == long_tx_id

    def test_payment_model_unicode_transaction_id(self) -> None:
        """Тест модели платежа с Unicode transaction_id."""
        unicode_tx_id = TestDomainIds.UNICODE_TX_ID
        payment = Payment(
            transaction_id=unicode_tx_id,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
        )

        assert payment.transaction_id == unicode_tx_id

    def test_payment_model_special_chars_transaction_id(self) -> None:
        """Тест модели платежа со специальными символами в transaction_id."""
        special_tx_id = TestDomainIds.SPECIAL_CHARS_TX_ID
        payment = Payment(
            transaction_id=special_tx_id,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
        )

        assert payment.transaction_id == special_tx_id

    def test_payment_model_very_large_amount(self) -> None:
        """Тест модели платежа с очень большой суммой."""
        large_amount = TestMonetaryConstants.AMOUNT_999999999999999_99
        payment = Payment(
            transaction_id=TestDomainIds.TX_BIG,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=large_amount,
        )

        assert payment.amount == large_amount

    def test_payment_model_very_small_amount(self) -> None:
        """Тест модели платежа с очень маленькой суммой."""
        small_amount = TestMonetaryConstants.AMOUNT_0_01
        payment = Payment(
            transaction_id=TestDomainIds.TX_SMALL,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=small_amount,
        )

        assert payment.amount == small_amount

    def test_payment_model_zero_amount(self) -> None:
        """Тест модели платежа с нулевой суммой."""
        payment = Payment(
            transaction_id=TestDomainIds.TX_ZERO,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_0_00,
        )

        assert payment.amount == TestMonetaryConstants.ZERO_TWO_PLACES

    def test_payment_model_negative_amount(self) -> None:
        """Тест модели платежа с отрицательной суммой."""
        negative_amount = TestMonetaryConstants.AMOUNT_NEG_100_00
        payment = Payment(
            transaction_id=TestDomainIds.TX_SPECIAL,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=negative_amount,
        )

        assert payment.amount == negative_amount

    def test_payment_model_high_precision_amount(self) -> None:
        """Тест модели платежа с высокой точностью суммы."""
        precise_amount = TestMonetaryConstants.PRECISE_123_123456789123456
        payment = Payment(
            transaction_id=TestDomainIds.TX_PRECISE,
            user_id=TestDomainIds.TEST_USER_ID,
            account_id=TestDomainIds.TEST_USER_ID,
            amount=precise_amount,
        )

        assert payment.amount == precise_amount

    def test_payment_model_negative_ids(self) -> None:
        """Тест модели платежа с отрицательными ID."""
        payment = Payment(
            transaction_id=TestDomainIds.TX_NEGATIVE_IDS,
            user_id=TestNumericConstants.NEGATIVE_ONE,
            account_id=TestNumericConstants.NEGATIVE_TWO,
            amount=TestMonetaryConstants.AMOUNT_100_00,
        )

        assert payment.user_id == TestNumericConstants.NEGATIVE_ONE
        assert payment.account_id == TestNumericConstants.NEGATIVE_TWO

    def test_payment_model_large_ids(self) -> None:
        """Тест модели платежа с большими ID."""
        large_id = TestDomainConstraints.MAX_INT32
        payment = Payment(
            transaction_id=TestDomainIds.TX_LARGE_IDS,
            user_id=large_id,
            account_id=large_id,
            amount=TestMonetaryConstants.AMOUNT_100_00,
        )

        assert payment.user_id == large_id
        assert payment.account_id == large_id
