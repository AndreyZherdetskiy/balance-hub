"""Тесты для синхронных валидаторов вебхука (без дублирования сервисной логики)."""

from __future__ import annotations


import pytest

from app.core.constants import ErrorMessages
from app.core.errors import ValidationError
from app.schemas.payment import WebhookPayment
from app.validators.sync.webhook import WebhookValidator
from app.utils.crypto import compute_signature
from tests.constants import TestDomainIds, TestTransactionData, TestMonetaryConstants


class TestWebhookValidator:
    """Покрываем только доменные ошибки и правильную проверку подписи."""

    def test_validate_payment_data_valid(self) -> None:
        """Валидные данные проходят без ошибок."""
        payload = WebhookPayment(
            transaction_id=TestDomainIds.WEBHOOK_TX_1,
            account_id=TestDomainIds.TEST_ACCOUNT_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature=TestTransactionData.SIGNATURE_GENERIC,
        )
        WebhookValidator.validate_payment_data(payload)

    def test_validate_payment_data_invalid_ids(self) -> None:
        """Неверные ID пользователя/счета — доменная ошибка."""
        payload = WebhookPayment(
            transaction_id=TestDomainIds.WEBHOOK_TX_1,
            account_id=TestDomainIds.TEST_ACCOUNT_ID,  # 0 — недопустим для валидатора
            user_id=0,
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature="ignored",
        )
        with pytest.raises(
            ValidationError, match=ErrorMessages.INVALID_USER_OR_ACCOUNT_ID
        ):
            WebhookValidator.validate_payment_data(payload)

    def test_validate_payment_data_invalid_tx_id(self) -> None:
        """Пустой transaction_id — доменная ошибка."""
        # Создаем payload с валидным transaction_id, но затем изменяем его
        payload = WebhookPayment(
            transaction_id=TestDomainIds.WEBHOOK_TX_1,
            account_id=TestDomainIds.TEST_ACCOUNT_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature=TestTransactionData.SIGNATURE_GENERIC,
        )
        # Изменяем transaction_id после создания (имитируем пустое значение)
        payload.transaction_id = ""

        with pytest.raises(ValidationError, match=ErrorMessages.INVALID_TRANSACTION_ID):
            WebhookValidator.validate_payment_data(payload)

    def test_validate_signature_valid(self) -> None:
        """Правильная подпись не вызывает ошибок."""
        secret = TestTransactionData.SECRET_KEY
        payload = WebhookPayment(
            transaction_id=TestDomainIds.WEBHOOK_TX_1,
            account_id=TestDomainIds.TEST_ACCOUNT_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature=compute_signature(
                account_id=TestDomainIds.TEST_ACCOUNT_ID,
                amount=TestMonetaryConstants.AMOUNT_100_00,
                transaction_id=TestDomainIds.WEBHOOK_TX_1,
                user_id=TestDomainIds.TEST_USER_ID,
                secret_key=secret,
            ),
        )
        WebhookValidator.validate_signature(payload, secret_key=secret)

    def test_validate_signature_invalid(self) -> None:
        """Неверная подпись должна приводить к доменной ошибке."""
        payload = WebhookPayment(
            transaction_id=TestDomainIds.WEBHOOK_TX_1,
            account_id=TestDomainIds.TEST_ACCOUNT_ID,
            user_id=TestDomainIds.TEST_USER_ID,
            amount=TestMonetaryConstants.AMOUNT_100_00,
            signature=TestTransactionData.INVALID_SIGNATURE,
        )
        with pytest.raises(ValidationError, match=ErrorMessages.INVALID_SIGNATURE):
            WebhookValidator.validate_signature(
                payload, secret_key=TestTransactionData.SECRET_KEY
            )

    def test_validate_payment_data_invalid_amount_via_stub(self) -> None:
        """Покрываем ветку `amount <= 0` через duck-typed stub (схема не пропускает 0)."""

        class PayloadStub:
            def __init__(self) -> None:
                self.transaction_id = TestDomainIds.WEBHOOK_TX_1
                self.account_id = TestDomainIds.TEST_ACCOUNT_ID
                self.user_id = TestDomainIds.TEST_USER_ID
                self.amount = TestMonetaryConstants.AMOUNT_0_00
                self.signature = TestTransactionData.SIGNATURE_GENERIC

        with pytest.raises(
            ValidationError, match=ErrorMessages.AMOUNT_MUST_BE_POSITIVE
        ):
            WebhookValidator.validate_payment_data(PayloadStub())
